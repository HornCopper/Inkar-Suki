import os

from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, build_path
from src.templates import HTMLSourceCode
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time

from ._template import recent_serendipity_head, recent_serendipity_row


async def get_recent_serendipity(server: str):
    params = {"server": server, "token": Config.jx3.api.token}
    data = (await Request(f"{Config.jx3.api.url}/data/event/recent", params=params).get()).json()
    if data["code"] != 200 or not data["data"]:
        return "未找到近期奇遇记录，请检查服务器后重试！"

    icons = {}
    for category in ("common", "peerless", "pet"):
        directory = build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", category])
        for filename in os.listdir(directory):
            icons[os.path.splitext(filename)[0]] = build_path(directory, [filename])

    rows = []
    for record in data["data"]:
        event_name = record["event"]
        rows.append(
            Template(recent_serendipity_row).render(
                role_name=record["name"],
                event_name=event_name,
                event_icon=icons[event_name] if event_name in icons else "",
                time=Time(record["time"]).format(),
                relative_time=Time().relate(record["time"]),
            )
        )
    html = str(
        HTMLSourceCode(
            application_name=f"近期奇遇 · {server}",
            table_head=recent_serendipity_head,
            table_body="\n".join(rows),
        )
    )
    return await generate(html, ".container", segment=True)
