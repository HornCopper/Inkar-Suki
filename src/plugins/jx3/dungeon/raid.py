from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, build_path
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request

from ._template import (
    image_template,
    table_zone_record_v2_head,
    template_zone_v2_record,
)

async def get_raid_records(server: str, role_name: str) -> dict:
    return (
        await Request(
            f"{Config.jx3.api.url}/raid/records",
            params = {
                "server": server,
                "name": role_name,
                "token": Config.jx3.api.token,
            },
        ).get()
    ).json()

async def get_raid_record_image(server: str, role_name: str):
    payload = await get_raid_records(server, role_name)
    records = payload.get("data")
    if payload.get("code") != 200 or not isinstance(records, list):
        return payload.get("msg") or "副本记录查询失败，请稍后重试！"
    if not records:
        return "该玩家目前尚未产生副本记录。"

    finished_icon = Template(image_template).render(
        image_path = build_path(ASSETS, ["image", "jx3", "cat", "grey.png"]),
    )
    available_icon = Template(image_template).render(
        image_path = build_path(ASSETS, ["image", "jx3", "cat", "gold.png"]),
    )
    rows = []
    for record in records:
        progress = record.get("bossProgress") or []
        rows.append(
            Template(template_zone_v2_record).render(
                zone_name = record.get("mapName") or "未知副本",
                images = "\n".join(
                    finished_icon if boss.get("finished") else available_icon for boss in progress
                    if isinstance(boss, dict)
                ),
            ),
        )

    source = str(
        HTMLSourceCode(
            application_name = f"副本记录 v2 · [{role_name}·{server}]",
            table_head = table_zone_record_v2_head,
            table_body = "\n".join(rows),
        ),
    )
    return await generate(source, ".container", segment = True)
