import html
import math
from typing import Any

from jinja2 import Template
from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.config import Config
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request

from ._template import SLRANK_TABLE_BODY, SLRANK_TABLE_HEAD


async def get_trial_rank(school: str, server: str):
    params = {"name": school, "token": Config.jx3.api.token}
    if server:
        params["server"] = server
    data = (
        await Request(
            f"{Config.jx3.api.url}/data/rank/trials",
            params=params,
        ).get()
    ).json()
    groups = [data["data"]] if isinstance(data["data"], dict) else data["data"]
    records = [
        (group["server"], record)
        for group in groups
        for record in group["data"]
    ]
    if not server:
        records.sort(
            key=lambda item: (
                item[1]["max_level"],
                item[1]["total_score"],
                item[1]["equip_score"],
            ),
            reverse=True,
        )
        records = records[:50]

    rows = [
        Template(SLRANK_TABLE_BODY).render(
            rank=rank,
            server=record_server,
            role_name=record["role_name"],
            level=record["max_level"],
            grade=f"{int(record['total_score']):,}",
            score=record["equip_score"],
        )
        for rank, (record_server, record) in enumerate(records, 1)
    ]
    source = str(
        HTMLSourceCode(
            application_name=f"试炼之地 · {server or '全服'} · {school}",
            table_head=SLRANK_TABLE_HEAD,
            table_body="\n".join(rows),
        )
    )
    return await generate(source, ".container", segment=True)


async def get_trial_dps(floor: int) -> ms | str:
    try:
        response = await Request(f"{Config.jx3.api.calculator_url}/trial").get(timeout=30)
        response.raise_for_status()
        data: Any = response.json()
        floor_data = next(row for row in data["rows"] if row["floor"] == floor)
    except StopIteration:
        return f"试炼血量接口中没有第 {floor} 层数据！"
    except Exception:
        return "试炼秒伤查询失败，请确认 calculator 服务可用后重试！"

    bosses = [
        (name, hp)
        for name, hp in floor_data.items()
        if name not in {"floor", "multiplier", "分身"}
    ]
    if not bosses or any(not isinstance(name, str) or not isinstance(hp, int) for name, hp in bosses):
        return "试炼血量接口返回的数据格式有误，请稍后重试！"

    rows = []
    for name, hp in bosses:
        clear_seconds, perfect_seconds = (178, 118) if name in {"子", "寅", "雷神"} else (298, 178)
        clear_hp = hp + 4 * floor_data["分身"] if name == "方鹤影" else hp
        perfect_hp = hp + 2 * floor_data["分身"] if name == "方鹤影" else hp
        rows.append(
            "<tr>"
            f"<td>{html.escape(name)}</td>"
            f"<td>{math.ceil(clear_hp / clear_seconds):,}</td>"
            f"<td>{math.ceil(perfect_hp / perfect_seconds):,}</td>"
            "</tr>"
        )

    source = str(
        HTMLSourceCode(
            application_name=f"试炼之地 · 第 {floor} 层 DPS",
            footer="计算时长已扣除 2s：子、寅、雷神 178s / 118s；其他首领 298s / 178s",
            table_head="<th>首领名</th><th>通关</th><th>完美</th>",
            table_body="".join(rows),
        )
    )
    return await generate(source, ".container", segment=True)
