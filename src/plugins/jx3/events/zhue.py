from jinja2 import Template

from src.config import Config
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.time import Time
from src.templates import HTMLSourceCode

from ._template import table_zhue_head, template_zhue

async def get_zhue_image(server: str):
    url = f"{Config.jx3.api.url}/data/server/antivice"
    params = {
        "server": server,
        "token": Config.jx3.api.token
    }
    data = (await Request(url, params=params).get()).json()
    tables = []
    for info in data["data"]:
        tables.append(
            Template(template_zhue).render(
                server = info["server"],
                map = info["map_name"],
                relate = Time().relate(info["time"])
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = f" · 诛恶事件 · {server}",
            table_head = table_zhue_head,
            table_body = "\n".join(tables)
        )
    )
    image = await generate(html, "table", segment=True)
    return image