from jinja2 import Template

from src.config import Config
from src.utils.network import Request
from src.utils.time import Time
from src.utils.decorators import token_required
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import (
    headers,
    template_item,
    table_item_head,
)

@token_required
async def get_item_record(name: str, token: str = ""):
    url = f"{Config.jx3.api.url}/reward/statistics"
    params = {
        "name": name,
        "token": token,
    }
    data = (await Request(url, params = params).get()).json()
    if data["code"] == 404:
        return "未找到相关物品，请检查物品名称是否正确！"
    tables = []
    for i in data["data"]:
        role_name = i["roleName"]
        item_name = i["itemName"]
        map_name = i["mapName"]
        pick_time = Time(i["time"]).format()
        relate_time = Time().relate(i["time"])
        server = i["server"]
        tables.append(
            Template(template_item).render(
                server = server,
                name = item_name,
                map = map_name,
                role = role_name,
                time = pick_time,
                relate = relate_time,
            ),
        )
    html = str(
        HTMLSourceCode(
            application_name = f"掉落统计 · 全服 · {name}",
            table_head = table_item_head,
            table_body = "\n".join(tables),
        ),
    )
    image = await generate(html, ".container", segment = True)
    return image
