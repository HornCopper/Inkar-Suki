from pathlib import Path
from jinja2 import Template
from typing import Any, List

from src.const.jx3.school import School
from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.const.path import (
    ASSETS,
    TEMPLATES,
    build_path
)
from src.utils.database import db
from src.utils.database.player import search_player
from src.utils.database.classes import Affections
from src.utils.time import Time
from src.utils.file import read
from src.utils.generate import generate

import random
    
def check_status(uin: int):
    data: Affections | None | Any = db.where_one(Affections(), "uin_1 = ? OR uin_2 = ?", uin, uin, default=None)
    if data is None:
        return False
    return True
    
async def get_school(name: str, server: str):
    data = await search_player(role_name=name, server_name=server)
    data = data.format_jx3api()
    if data["code"] != 200:
        return False
    else:
        return data["data"]["forceName"]

async def bind_affection(uin_1: int, name_1: str, uin_2: int, name_2: str, group_id: int, custom_time: int):
    if check_status(uin_1) or check_status(uin_2):
        return [PROMPT.AffectionExist]
    server = Server(None, group_id).server
    if not server:
        return [PROMPT.ServerNotExist]
    school_1 = await get_school(name_1, server)
    school_2 = await get_school(name_2, server)
    if not school_1 or not school_2:
        return [PROMPT.AffectionRoleNotExist]
    new_data = Affections(
        server = server,
        uin_1 = uin_1,
        uin_2 = uin_2,
        name_1 = name_1,
        name_2 = name_2,
        time = custom_time,
        school_1 = school_1,
        school_2 = school_2
    )
    db.save(new_data)
    return [PROMPT.AffectionBindComplete]

async def delete_affection(uin: int) -> List[str] | None:
    if not check_status(uin):
        return [PROMPT.AffectionUnbindWithNo]
    db.delete(Affections(), "uin_1 = ? OR uin_2 = ?", (uin, uin))

async def generate_affection_image(uin: int):
    if not check_status(uin):
        return [PROMPT.AffectionGenerateWithNo]
    current_data: Affections | Any = db.where_one(Affections(), "uin_1 = ? OR uin_2 = ?", uin, uin, default=None)
    btxbfont = build_path(
        ASSETS,
        [
            "font", 
            "包图小白体.ttf"
        ]
    )
    yozaifont = build_path(
        ASSETS,
        [
            "font", 
            "Yozai-Medium.ttf"
        ]
    )
    bg = build_path(
        ASSETS,
        [
            "image",
            "assistance"
        ],
        end_with_slash=True
    ) + str(random.randint(1, 9)) + ".jpg"
    uin_1 = current_data.uin_1
    uin_2 = current_data.uin_2
    color_1 = School(current_data.school_1).color
    color_2 = School(current_data.school_2).color
    img_1 = School(current_data.school_1).icon
    img_2 = School(current_data.school_2).icon
    name_1 = current_data.name_1
    name_2 = current_data.name_2
    server = current_data.server
    recognization = Time(current_data.time).format()
    if not isinstance(recognization, str):
        return
    relate = Time().relate(current_data.time)[:-1]
    html = read(
        build_path(
            TEMPLATES,
            [
                "jx3",
                "affections.html"
            ]
        )
    )
    html = Template(html).render(
        btxbfont=btxbfont,
        yozaifont=yozaifont,
        bg=bg,
        uin_1=str(uin_1),
        uin_2=str(uin_2),
        color_1=color_1,
        color_2=color_2,
        img_1=img_1,
        img_2=img_2,
        name_1=name_1,
        name_2=name_2,
        server=server,
        recognization=recognization,
        relate=relate,
    )
    final_path = await generate(html, ".background-container", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()