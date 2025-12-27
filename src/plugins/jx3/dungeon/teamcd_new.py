from jinja2 import Template
from itertools import chain
from typing import Any
from collections import Counter

from src.config import Config
from src.const.jx3.school import School
from src.const.prompts import PROMPT
from src.const.path import ASSETS, CONST, build_path
from src.utils.database import db
from src.utils.database.classes import PersonalSettings, RoleData
from src.utils.database.player import search_player
from src.utils.tuilan import generate_timestamp, generate_dungeon_sign
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.file import read
from src.templates import HTMLSourceCode, SimpleHTML, get_saohua

from ._template import (
    image_template,
    template_zone_v2_record,
    table_zone_record_v2_head
)

async def get_zone_record_image(server: str, role: str):
    role_info = await search_player(role_name=role, server_name=server)
    guid = role_info.globalRoleId
    if guid == "":
        return PROMPT.PlayerNotExist
    url = read(CONST + "/cache/teamcd.txt")
    params = {
        "server": server,
        "name": role
    }
    data = (await Request(url, params=params).get()).json()
    unable = Template(image_template).render(
        image_path = build_path(ASSETS, ["image", "jx3", "cat", "grey.png"])
    )
    available = Template(image_template).render(
        image_path = build_path(ASSETS, ["image", "jx3", "cat", "gold.png"])
    )
    if data["code"] != 200:
        return PROMPT.PlayerNotExist
    else:
        contents = []
        for i in data["data"]["detail"]:
            images = []
            map_name = i["mapName"]
            for x in i["bossProgress"]:
                if x["finished"] is True:
                    images.append(unable)
                else:
                    images.append(available)
            image_content = "\n".join(images)
            contents.append(
                Template(template_zone_v2_record).render(
                    zone_name = map_name,
                    images = image_content
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f"副本记录 · [{role}·{server}]",
                table_head = table_zone_record_v2_head,
                table_body = "\n".join(contents)
            )
        )
        image = await generate(html, ".container", segment=True)
        return image