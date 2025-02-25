from pathlib import Path
from jinja2 import Template
from nonebot.adapters.onebot.v11 import Bot

from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.file import read
from src.utils.database.operation import get_group_settings
from src.utils.generate import generate
from src.templates import SimpleHTML

from ._template import template_subscribe

import json

async def generate_group_info(bot: Bot, group_id: str):
    subscribe_options = json.loads(read(build_path(ASSETS, ["source", "subscribe"], end_with_slash=True) + "options.json"))
    additions_options = json.loads(read(build_path(ASSETS, ["source", "subscribe"], end_with_slash=True) + "additions.json"))
    current_subscribe = get_group_settings(group_id, "subscribe")
    current_additions = get_group_settings(group_id, "additions")
    subscribe_contents = []
    additions_contents = []
    for i in list(subscribe_options):
        desc = subscribe_options[i][0]
        icon = Path(ASSETS + "/image/subscribes/" + subscribe_options[i][1]).as_uri()
        if i in current_subscribe:
            status = "enabled"
            flag = "✔"
        else:
            status = "disabled"
            flag = "✖"
        subscribe_contents.append(
            Template(template_subscribe).render(
                image = icon,
                subject = i,
                description = desc,
                status = status,
                flag = flag
            )
        )
    for i in list(additions_options):
        desc = additions_options[i][0]
        icon = Path(ASSETS + "/image/subscribes/" + additions_options[i][1]).as_uri()
        if i in current_additions:
            status = "enabled"
            flag = "✔"
        else:
            status = "disabled"
            flag = "✖"
        additions_contents.append(
            Template(template_subscribe).render(
                image = icon,
                subject = i,
                description = desc,
                status = status,
                flag = flag
            )
        )
    final_subscribe_contents = "\n".join(subscribe_contents)
    final_additions_contents = "\n".join(additions_contents)
    group_info = await bot.call_api("get_group_info", group_id=int(group_id))
    group_name = group_info["group_name"]
    html = str(
        SimpleHTML(
            "jx3",
            "subscribe.html",
            css_ = Path(build_path(TEMPLATES, ["jx3", "subscribe.css"])),
            font = build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
            subscribe_contents = final_subscribe_contents,
            additions_contents = final_additions_contents,
            group_id = group_id,
            group_name = group_name,
            grass_image = Path(build_path(ASSETS, ["image", "minecraft", "grass.png"])).as_uri()
        )
    )
    image = await generate(html, ".total", segment=True)
    return image