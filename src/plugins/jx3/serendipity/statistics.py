from jinja2 import Template

from src.config import Config
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time

from ._template import statistics_serendipity_head, statistics_serendipity_row


async def get_serendipity_statistics(server: str, event_name: str):
    params = {"name": event_name, "token": Config.jx3.api.token}
    if server:
        params["server"] = server
    data = (await Request(f"{Config.jx3.api.url}/data/event/statistics", params=params).get()).json()
    if data["code"] != 200 or not data["data"]:
        return "未找到该奇遇的统计记录，请检查服务器和奇遇名称后重试！"

    rows = []
    for record in data["data"]:
        rows.append(
            Template(statistics_serendipity_row).render(
                server=record["server"],
                role_name=record["name"],
                time=Time(record["time"]).format(),
                relative_time=Time().relate(record["time"]),
            )
        )
    html = str(
        HTMLSourceCode(
            application_name=f"奇遇统计 · {server or '全服'} · {event_name}",
            table_head=statistics_serendipity_head,
            table_body="\n".join(rows),
        )
    )
    return await generate(html, ".container", segment=True)
