from jinja2 import Template
from pathlib import Path

from src.const.path import (
    TEMPLATES,
    build_path
)
from src.const.prompts import PROMPT
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.database.player import search_player
from src.templates import HTMLSourceCode

from ._template import table_head, template_body

async def get_progress_v2(
    server: str = "", 
    name: str = "", 
    achievement: str = ""
):
    personal_data_request = await search_player(role_name=name, server_name=server)
    personal_data = personal_data_request.format_jx3api()
    if personal_data["code"] != 200:
        guid = ""
        return ["唔……玩家信息获取失败。"]
    else:
        guid = personal_data["data"]["globalRoleId"]
    params = {
        "size": 200,
        "gameRoleId": guid,
        "name": achievement
    }
    data = (await Request("https://m.pvp.xoyo.com/achievement/list/achievements", params=params).post(tuilan=True)).json()
    data = data["data"]["data"]
    if len(data) == 0:
        return ["唔……未找到相关成就。"]
    else:
        contents = []
        for i in data:
            contents.append(
                Template(template_body).render(
                    image = i["icon"],
                    name = i["name"],
                    type = i["detail"],
                    desc = i["desc"],
                    value = i["reward_point"],
                    status = "correct" if i["isFinished"] else "incorrect",
                    flag = "✔" if i["isFinished"] else "✖"
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f" · 成就百科 · {server} · {name} · {achievement}",
                additional_css = Path(
                    build_path(
                        TEMPLATES,
                        [
                            "jx3",
                            "achievements_v2.css"
                        ]
                    )
                ).as_uri(),
                table_head = table_head,
                table_body = "\n".join(contents)
            )
        )
        final_path = await generate(html, "table", False)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()
    
async def get_map(
    name: str,
    mode: str
) -> str | None:
    params = {
        "mode": 2
    }
    data = (await Request(url="https://m.pvp.xoyo.com/dungeon/list", params=params).post(tuilan=True)).json()
    for i in data["data"]:
        for x in i["dungeon_infos"]:
            if x["name"] == name:
                for y in x["maps"]:
                    if y["mode"] == mode:
                        return y["map_id"]

async def zone_achievement(
        server: str = "", 
        name: str = "", 
        zone: str = "", 
        mode: str = ""
    ) -> str | None | list:
    personal_data_request = await search_player(role_name=name, server_name=server)
    personal_data = personal_data_request.format_jx3api()
    if personal_data["code"] != 200:
        guid = ""
        return [PROMPT.PlayerNotExist]
    else:
        guid = personal_data["data"]["globalRoleId"]
    map_id = await get_map(zone, mode)
    if not isinstance(map_id, str):
        return
    params = {
        "cursor": 0,
        "size": 200,
        "dungeon_map_id": int(map_id),
        "gameRoleId": guid
    }
    data = (await Request("https://m.pvp.xoyo.com/achievement/list/achievements", params=params).post(tuilan=True)).json()
    data = data["data"]["data"]
    if len(data) == 0:
        return ["唔……未找到相关成就。"]
    else:
        contents = []
        for i in data:
            contents.append(
                Template(template_body).render(
                    image = i["icon"],
                    name = i["name"],
                    type = i["detail"],
                    desc = i["desc"],
                    value = i["reward_point"],
                    status = "correct" if i["isFinished"] else "incorrect",
                    flag = "✔" if i["isFinished"] else "✖"
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f" · 成就百科 · {server} · {name} · {mode}{zone}",
                additional_css = Path(
                    build_path(
                        TEMPLATES,
                        [
                            "jx3",
                            "achievements_v2.css"
                        ]
                    )
                ).as_uri(),
                table_head = table_head,
                table_body = "\n".join(contents)
            )
        )
        final_path = await generate(html, "table", False)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()
