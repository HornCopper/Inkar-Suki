from datetime import datetime
from pathlib import Path
from jinja2 import Template

from src.config import Config
from src.const.prompts import PROMPT
from src.const.path import ASSETS, build_path
from src.utils.network import Request
from src.utils.time import Time
from src.utils.database.player import search_player
from src.utils.generate import generate
from src.templates import SimpleHTML

from ._template import template_serendity, poem
from .without_jx3api import JX3Serendipity

import os

token = Config.jx3.api.token
ticket = Config.jx3.api.ticket
bot_name = Config.bot_basic.bot_name_argument

Serendipity = JX3Serendipity()

async def get_serendipity_v2(server: str, name: str, type: bool):
    role_data = await search_player(role_name=name, server_name=server)
    if role_data.format_jx3api()["code"] != 200:
        return [PROMPT.PlayerNotExist]
    if Config.jx3.api.enable:
        serendipity_data = (await Request(f"{Config.jx3.api.url}/data/luck/adventure?server={server}&name={name}&ticket={ticket}&token={token}").get()).json()
        serendipity_data = serendipity_data["data"]
    else:
        serendipity_data = await Serendipity.integration(server, name)
    data = serendipity_data
    # 笔记：1 → 世界奇遇；2 → 绝世奇遇；3 → 宠物奇遇
    # 注：暂时忽略宠物奇遇，不做统计
    tables = []
    current_time = int(datetime.now().timestamp())
    type_map = ["common", "peerless", "pet"]
    for i in data:
        if type and i["level"] >= 3: # 绝世+普通
            continue
        if not type and i["level"] != 3: # 宠物
            continue
        serendipity_name = i["name"]
        flag = build_path(ASSETS, ["image", "jx3", "serendipity", "vector", "peerless.png"]) if i["level"] == 2 else ""
        icon = build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", type_map[i["level"]-1]], end_with_slash=True) + serendipity_name + ".png"
        if not os.path.exists(icon):
            continue
        if i["time"] != 0:
            time_gotten = Time(i["time"]).format("%Y-%m-%d %H:%M:%S")
            relate_time = Time().relate(i["time"])
        else:
            time_gotten = "遗忘的时间"
            relate_time = ""
        tables.append(
            Template(template_serendity).render(
                peerless_flag = flag,
                serendipity_icon = icon,
                actual_time = str(time_gotten),
                relative_time = relate_time,
                serendipity_name = serendipity_name
            )
        )
    if len(tables) == 0:
        return ["唔……您似乎只有宠物奇遇哦。"]
    tables[0] = tables[0][:-5] + poem + "</tr>"
    html = str(
        SimpleHTML(
            "jx3",
            "serendipity_v2",
            font = build_path(ASSETS, ["font", "custom.ttf"]),
            table_content = "\n".join(tables),
            app_info = f"个人奇遇记录 · {server} · {name} · " + Time().format("%H:%M:%S"),
            title_image = build_path(ASSETS, ["image", "jx3", "serendipity", "vector", "title.png"]),
            poem_image = build_path(ASSETS, ["image", "jx3", "serendipity", "vector", "poem.png"])
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()
