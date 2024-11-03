from pathlib import Path
from jinja2 import Template
from json.decoder import JSONDecodeError
from typing import Literal

from src.const.jx3.constant import dungeon_name_data as map_list
from src.const.path import build_path, TEMPLATES
from src.const.prompts import PROMPT
from src.utils.database.player import search_player
from src.utils.network import Request
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import (
    table_zone_detail_header,
    table_zone_overview_header,
    template_zone_detail,
    template_zone_detail_header,
    template_zone_overview
)

async def get_guid(server: str, name: str) -> Literal[False] | str:
    if not isinstance(server, str):
        return
    data = await search_player(role_name=name, server_name=server)
    data = data.format_jx3api()
    if data["code"] != 200:
        return False
    else:
        return data["data"]["globalRoleId"]


async def get_menu() -> Literal[False] | list:
    menu_data = (await Request("https://m.pvp.xoyo.com/achievement/list/menu").post(tuilan=True)).json()
    for i in menu_data["data"]:
        if i["name"] == "江湖行":
            for x in i["subClass"]:
                if x["name"] == "秘境":
                    categories = []
                    for y in x["detailClass"]:
                        categories.append(y["name"])
                    return categories
            return False
    return False


async def get_total_data(guid: str) -> dict:
    params = {
        "gameRoleId": guid,
        "cursor": 0,
        "size": 10000,
        "class": "江湖行",
        "sub_class": "秘境",
        "detail": "",
    }
    data = (await Request("https://m.pvp.xoyo.com/achievement/list/achievements", params=params).post(tuilan=True)).json()
    return data

async def get_value(data: dict, detail: str) -> tuple[str, str]:
    filtered_data = {"data": [e for e in data["data"]["data"] if e["detail"] == detail]}
    total = 0
    finished = 0
    for i in filtered_data["data"]:
        if i["isFinished"]:
            finished = finished + i["reward_point"]
        total = total + i["reward_point"]
    return f"{finished}/{total}", str(int(finished/total*100)) + "%"


def get_color_type(proportion: str) -> str:
    num = int(proportion[0:-1])
    if 0 <= num < 25:
        return "0"
    elif 25 <= num < 50:
        return "25"
    elif 50 <= num < 75:
        return "50"
    elif 75 <= num < 100:
        return "75"
    elif num == 100:
        return "100"
    else:
        raise ValueError(f"Unsupport value {num} appeared in the proportion!")


async def get_zone_overview_image(server: str, id: str) -> list[str] | str | None:
    detail = await get_menu()
    if not detail:
        return ["唔……获取目录失败！"]
    guid = await get_guid(server, id)
    if not guid:
        return ["唔……未查找到该玩家！"]
    content = []
    data = await get_total_data(guid)
    for i in detail:
        name = i
        filtered_data = await get_value(data, name)
        value = filtered_data[0]
        proportion = str(filtered_data[1])
        relate = get_color_type(proportion)
        content.append(
            Template(template_zone_overview).render(
                name = name,
                relate_proportion = relate,
                proportion = proportion,
                value = value
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = f" · 副本总览 · {server} · {name}",
            additional_css = Path(
                build_path(
                    TEMPLATES,
                    [
                        "jx3",
                        "zone_overview.css"
                    ]
                )
            ).as_uri(),
            table_head = table_zone_overview_header,
            table_body = "\n".join(content)
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()

def get_map_all_id(data: dict, map_name: str) -> list[dict]:
    for zone in data["data"]:
        if zone["name"] == map_name:
            return zone["maps"]
    raise ValueError(f"Cannot match the zone `{map_name}`!")

def calculate(raw_data: dict) -> tuple[int, int]:
    done = 0
    total = 0
    for achievement in raw_data["data"]["data"]:
        if achievement["isFinished"]:
            done += achievement["reward_point"]
        total += achievement["reward_point"]
    return done, total

async def get_zone_detail_image(server: str, name: str, team: bool = True):
    guid = await get_guid(server, name)
    if not guid:
        return [PROMPT.PlayerNotExist]
    table = []
    map_id_data: dict = (await Request("https://m.pvp.xoyo.com/achievement/list/dungeon-maps", params={"detail": True}).post(tuilan=True)).json()
    for map in map_list:
        if map in ["一之窟", "天龙寺", "冰川宫宝库", "风砂旧垒", "不染窟"]:
            continue # 丝路风语
        map_data: list[dict[str, str]] = get_map_all_id(map_id_data, map) # actually list[dict[str, str | int]]
        if map_data[0]["name"].startswith("5人") == team:
            continue
        mode_count = len(map_data)
        is_first = True
        for mode in map_data:
            if is_first:
                template = template_zone_detail.replace(
                    "{{ header }}", 
                    Template(template_zone_detail_header).render(
                        count = str(mode_count),
                        name = map
                    )
                )
                is_first = False
            else:
                template = template_zone_detail.replace(
                    "{{ header }}", 
                    ""
                )
            params = {
                "cursor": 0, 
                "size": 200, 
                "dungeon_map_id": mode["id"], 
                "gameRoleId": guid
            }
            try:
                single_map_data = (await Request("https://m.pvp.xoyo.com/achievement/list/achievements", params=params).post(tuilan=True)).json()
                done, total = calculate(single_map_data)
                schedule = str(int(done / total * 100)) + "%"
            except JSONDecodeError:
                try:
                    single_map_data = (await Request("https://m.pvp.xoyo.com/achievement/list/achievements", params=params).post(tuilan=True)).json()
                    done, total = calculate(single_map_data)
                    schedule = str(int(done / total * 100)) + "%"
                except JSONDecodeError:
                    done, total = 0, 1
                    schedule = "获取失败！"
            table.append(
                Template(template).render(
                    mode = mode["name"],
                    schedule = schedule,
                    num = f"{done}/{total}"
                )
            )
    html = str(
        HTMLSourceCode(
            application_name = f" · 副本分览 · {server} · {name}",
            additional_css = Path(
                build_path(
                    TEMPLATES,
                    [
                        "jx3",
                        "zone_detail.css"
                    ]
                )
            ).as_uri(),
            additional_js = Path(
                build_path(
                    TEMPLATES,
                    [
                        "jx3",
                        "zone_detail.js"
                    ]
                )
            ),
            table_head = table_zone_detail_header,
            table_body = "\n".join(table)
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()