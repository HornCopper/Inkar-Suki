from jinja2 import Template

from src.config import Config
from src.utils.jx3api import jx3api_get
from src.utils.generate import generate
from src.utils.time import Time
from src.templates import HTMLSourceCode

from ._template import table_zhue_head, template_zhue

async def get_zhue_image(server: str):
    url = '/wicked/records'
    params = {
        "server": server,
        "token": Config.jx3.api.token_v2,
    }
    data = await jx3api_get(url, params = params)
    if data["code"] != 200:
        return data["msg"] or "诛恶事件查询失败，请稍后重试！"
    tables = []
    for info in data["data"]:
        tables.append(
            Template(template_zhue).render(
                server = info["server"],
                map = info["mapName"],
                relate = Time().relate(info["time"]),
            ),
        )
    html = str(
        HTMLSourceCode(
            application_name = f"诛恶事件 · {server}",
            table_head = table_zhue_head,
            table_body = "\n".join(tables),
        ),
    )
    image = await generate(html, ".container", segment = True)
    return image
