from jinja2 import Template

from src.config import Config
from src.utils.decorators import token_required
from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import (
    template_firework,
    template_firework_head
)

async def get_firework_record(server: str, name: str):
    url = f"{Config.jx3.api.url}/data/show/records"
    params = {
        "token": Config.jx3.api.token_v2,
        "server": server,
        "name": name
    }
    data = (await Request(url, params=params).get()).json()
    if data["code"] == 404:
        return "没有找到相关烟花记录，请检查后重试！"
    table = []
    for record in data["data"]:
        table.append(
            Template(template_firework).render(
                server=record["server"],
                sender=record["sender"],
                receiver=record["receiver"],
                map_name=record["map_name"],
                firework=record["firework"],
                time=Time(record["time"]).format()
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = f"烟花记录 · [{name}·{server}]",
            table_head = template_firework_head,
            table_body = "\n".join(table)
        )
    )
    image = await generate(html, ".container", segment=True)
    return image