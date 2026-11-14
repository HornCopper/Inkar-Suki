import html
import math
from typing import Any

from jinja2 import Template
from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.config import Config
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.jx3api import jx3api_get

from ._template import SLRANK_TABLE_BODY, SLRANK_TABLE_HEAD

async def get_trial_rank(school: str, server: str):
    # The PC 藏剑 board combines both sword stances; 悟 has its own full name.
    kungfu = "藏剑" if school in {"问水诀", "山居剑意"} else school
    params = {"kungfu": kungfu, "token": Config.jx3.api.token}
    if server:
        params["server"] = server
    data = await jx3api_get(
        "/rank/trials",
        params = params,
    )
    if data["code"] != 200 or not data["data"]:
        return data["msg"] or "未找到该心法的试炼榜单，请检查服务器和心法名称后重试！"
    groups = [data["data"]] if isinstance(data["data"], dict) else data["data"]
    records = []
    # The current client payload uses numeric keys for the four visible columns.
    fields = {"roleName": "1", "maxLevel": "2", "totalScore": "3", "equipScore": "4"}
    for group in groups:
        for raw_record in group["data"]:
            record = dict(raw_record)
            for field, client_field in fields.items():
                if field not in record and client_field in record:
                    record[field] = record[client_field]
            records.append((group["server"], record))
    if not server:
        records.sort(
            key = lambda item: (
                item[1]["maxLevel"],
                item[1]["totalScore"],
                item[1]["equipScore"],
            ),
            reverse = True,
        )
        records = records[:50]

    rows = [
        Template(SLRANK_TABLE_BODY).render(
            rank = rank,
            server = record_server,
            role_name = record["roleName"],
            level = record["maxLevel"],
            grade = f"{int(record['totalScore']):,}",
            score = record["equipScore"],
        ) for rank, (record_server, record) in enumerate(records, 1)
    ]
    source = str(
        HTMLSourceCode(
            application_name = f"试炼之地 · {server or '全服'} · {school}",
            table_head = SLRANK_TABLE_HEAD,
            table_body = "\n".join(rows),
        ),
    )
    return await generate(source, ".container", segment = True)

async def get_trial_dps(floor: int) -> ms | str:
    try:
        response = await Request(f"{Config.jx3.api.calculator_url}/trial").get(timeout = 30)
        response.raise_for_status()
        data: Any = response.json()
        floor_data = next(row for row in data["rows"] if row["floor"] == floor)
    except StopIteration:
        return f"试炼血量接口中没有第 {floor} 层数据！"
    except Exception:
        return "试炼秒伤查询失败，请确认 calculator 服务可用后重试！"

    bosses = [(name, hp) for name, hp in floor_data.items() if name not in {"floor", "multiplier", "分身"}]
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
            "</tr>",
        )

    source = str(
        HTMLSourceCode(
            application_name = f"试炼之地 · 第 {floor} 层 DPS",
            footer = "计算时长已扣除 2s：子、寅、雷神 178s / 118s；其他首领 298s / 178s",
            table_head = "<th>首领名</th><th>通关</th><th>完美</th>",
            table_body = "".join(rows),
        ),
    )
    return await generate(source, ".container", segment = True)
