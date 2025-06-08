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

def get_map_all_id(data: dict, map_name: str) -> list[dict]:
    for zone in data["data"]:
        if zone["name"] == map_name:
            return zone["maps"]
    raise ValueError(f"Cannot match the zone `{map_name}`!")

async def get_progress_v2(
    server: str = "", 
    name: str = "", 
    achievement: str = ""
):
    personal_data_request = await search_player(role_name=name, server_name=server)
    personal_data = personal_data_request.format_jx3api()
    if personal_data["code"] != 200:
        guid = ""
        return PROMPT.PlayerNotExist
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
        return "唔……未找到相关成就。"
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
                    flag = "✔" if i["isFinished"] else "✖",
                    current = i["currentValue"],
                    target = i["triggerValue"],
                    progress = str(round(i["currentValue"] / i["triggerValue"], 4) * 100)
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f"成就百科 · [{name}·{server}] · {achievement}",
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
        image = await generate(html, ".container", segment=True)
        return image
    
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
    ):
    personal_data_request = await search_player(role_name=name, server_name=server)
    personal_data = personal_data_request.format_jx3api()
    if personal_data["code"] != 200:
        guid = ""
        return PROMPT.PlayerNotExist
    else:
        guid = personal_data["data"]["globalRoleId"]
    map_id_data: dict = (await Request("https://m.pvp.xoyo.com/achievement/list/dungeon-maps", params={"detail": True}).post(tuilan=True)).json()
    map_id = get_map_all_id(map_id_data, zone)
    flag = False
    for each_map_id in map_id:
        if each_map_id["name"] == mode:
            _map_id = each_map_id["id"]
            flag = True
    if not flag:
        return "未找到相关副本信息！"
    params = {
        "cursor": 0,
        "size": 200,
        "dungeon_map_id": int(_map_id),
        "gameRoleId": guid
    }
    data = (await Request("https://m.pvp.xoyo.com/achievement/list/achievements", params=params).post(tuilan=True)).json()
    data = data["data"]["data"]
    if len(data) == 0:
        return "唔……未找到相关成就。"
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
                    flag = "✔" if i["isFinished"] else "✖",
                    current = i["currentValue"],
                    target = i["triggerValue"]
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f"成就百科 · [{name}·{server}] · {mode}{zone}",
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
        image = await generate(html, ".container", segment=True)
        return image
