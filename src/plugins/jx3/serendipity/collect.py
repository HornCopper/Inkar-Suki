import os
from pathlib import Path
from random import choice

from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, build_path
from src.templates import SimpleHTML
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time

from ._template import collect_serendipity_card, collect_serendipity_row


async def get_serendipity_collect(server: str, days: int):
    params = {"server": server, "num": days, "token": Config.jx3.api.token}
    data = (await Request(f"{Config.jx3.api.url}/data/event/collect", params=params).get()).json()
    if data["code"] != 200 or not data["data"]:
        return "未找到奇遇汇总记录，请检查服务器后重试！"

    assets = {}
    for category in ("common", "peerless", "pet"):
        directory = build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", category])
        for filename in os.listdir(directory):
            assets[os.path.splitext(filename)[0]] = category

    records = sorted(data["data"], key=lambda record: 0 if record["event"] in assets and assets[record["event"]] == "peerless" else 1)
    cards = []
    for record in records:
        event_name = record["event"]
        latest = record["data"]
        category = assets[event_name] if event_name in assets else "common"
        show_path = build_path(ASSETS, ["image", "jx3", "serendipity", "show", category, f"{event_name}.png"])
        name_path = build_path(ASSETS, ["image", "jx3", "serendipity", "name", f"{event_name}.png"])
        if category == "peerless" and not Path(show_path).exists():
            backgrounds = list(Path(show_path).parent.glob(f"{event_name}-*.png"))
            if backgrounds:
                show_path = choice(backgrounds).as_posix()
        cards.append(
            Template(collect_serendipity_card).render(
                event_name=event_name,
                show_path=show_path if Path(show_path).exists() else "",
                name_path=name_path if Path(name_path).exists() else "",
                peerless_icon=(
                    build_path(ASSETS, ["image", "jx3", "serendipity", "vector", "peerless.png"])
                    if category == "peerless" else ""
                ),
                count=record["count"],
                role_name=latest["name"],
                time=Time(latest["time"]).format(),
                relative_time=Time().relate(latest["time"]),
            )
        )
    rows = [Template(collect_serendipity_row).render(cards="\n".join(cards[i:i + 7])) for i in range(0, len(cards), 7)]
    html = str(
        SimpleHTML(
            "jx3",
            "serendipity_collect.html",
            font=build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
            ink_background=build_path(ASSETS, ["image", "jx3", "serendipity", "vector", "background.png"]),
            server=server,
            days=days,
            total=sum(record["count"] for record in data["data"]),
            rows="\n".join(rows),
        )
    )
    return await generate(html, ".collect-card", segment=True)
