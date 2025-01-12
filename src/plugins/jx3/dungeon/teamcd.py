from jinja2 import Template
from itertools import chain
from typing import Any
from pathlib import Path
from collections import Counter

from src.const.jx3.school import School
from src.const.prompts import PROMPT
from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.database import db
from src.utils.database.classes import PersonalSettings, RoleData
from src.utils.database.player import search_player
from src.utils.tuilan import generate_timestamp, generate_dungeon_sign
from src.utils.generate import generate
from src.utils.network import Request
from src.templates import HTMLSourceCode

from ._template import (
    image_template,
    template_zone_record,
    table_zone_record_head
)

def sort_role_daa(objects: list[RoleData]) -> list[RoleData]:
    server_counts = Counter(obj.serverName for obj in objects)
    return sorted(objects, key=lambda obj: server_counts[obj.serverName], reverse=True)

def build_teamcd_request(guid: str) -> Request:
    ts = generate_timestamp()
    params = {
        "globalRoleId": guid,
        "sign": generate_dungeon_sign(f"globalRoleId={guid}&ts={ts}"),
        "ts": ts
    }
    return Request("https://m.pvp.xoyo.com/h5/parser/cd-process/get-by-role", params=params)

async def get_zone_record_image(server: str, role: str):
    data = await search_player(role_name=role, server_name=server)
    details_data = data.format_jx3api()
    if details_data["code"] != 200:
        guid = ""
        return PROMPT.PlayerNotExist
    else:
        guid = details_data["data"]["globalRoleId"]
    request = build_teamcd_request(guid)
    data = (await request.post(tuilan=True)).json()
    unable = Template(image_template).render(
        image_path = build_path(ASSETS, ["image", "jx3", "cat", "grey.png"])
    )
    available = Template(image_template).render(
        image_path = build_path(ASSETS, ["image", "jx3", "cat", "gold.png"])
    )
    if data["data"] == []:
        return "该玩家目前尚未打过任何副本哦~\n注意：10人普通副本会在周五刷新一次。"
    else:
        contents = []
        if data is None:
            return PROMPT.PlayerNotExist
        for i in data["data"]:
            images = []
            map_name = i["mapName"]
            map_type = i["mapType"]
            for x in i["bossProgress"]:
                if x["finished"] is True:
                    images.append(unable)
                else:
                    images.append(available)
            image_content = "\n".join(images)
            contents.append(
                Template(template_zone_record).render(
                    zone_name = map_name,
                    zone_mode = map_type,
                    images = image_content
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f" · 副本记录 · {server} · {role}",
                table_head = table_zone_record_head,
                table_body = "\n".join(contents)
            )
        )
        image = await generate(html, "table", segment=True)
        return image
    
def parse_data(data) -> dict:
    result = {}
    for entry in data["data"]:
        map_type = entry["mapType"]
        map_name = entry["mapName"]
        boss_progress = entry["bossProgress"]
        progress_finished = [boss["finished"] for boss in boss_progress]
        key = f"{map_type}{map_name}"
        result[key] = progress_finished
    return result

def synchronize_keys(data: list[list[dict[str, list[bool]]]]) -> list[list[dict[str, list[bool]]]]:
    all_keys = set(k for sublist in data for d in sublist for k in d.keys())
    for sublist in data:
        current_keys: set[str] = set(k for d in sublist for k in d.keys())
        missing_keys: set[str] = all_keys - current_keys
        for key in missing_keys:
            value_length = max(len(d[key]) for sublist_inner in data for d in sublist_inner if key in d)
            for d in sublist:
                if key not in d:
                    d[key] = [False] * value_length
    return data

    
async def get_mulit_record_image(server: str, roles: list[str]):
    not_found_roles: list[str] = []
    found_roles: list[str] = []
    for each_role in roles:
        role_data = await search_player(
            role_name = each_role,
            server_name = server,
            local_lookup = True
        )
        role_data = role_data.format_jx3api()
        if role_data["code"] == 404:
            not_found_roles.append(each_role)
        else:
            found_roles.append(role_data["data"]["globalRoleId"])
    if len(not_found_roles) > 0:
        return "有以下角色尚未存在于音卡的数据库中，请提交角色！\n" + "\n".join(not_found_roles)
    responses = [
        (await request.post(tuilan=True)).json()
        for request
        in [
            build_teamcd_request(each_guid)
            for each_guid
            in found_roles
        ]
    ]
    roles_data: list[list[dict[str, list[bool]]]] = [[] for _ in range(len(found_roles))]
    num = 0
    for each_response in responses:
        roles_data[num].append(parse_data(each_response))
        num += 1
    final_data = synchronize_keys(roles_data)
    zones: list[str] = list(set(chain.from_iterable(d.keys() for sublist in final_data for d in sublist)))
    table_head = "<tr><th class=\"short-column\">角色</th>" + "\n".join([f"<th class=\"short-column\">{zone}</th>" for zone in zones]) + "</tr>"
    tables: list[str] = []
    num = 0
    for each_role_data in roles_data:
        data = each_role_data[0]
        row = ["<td class=\"short-column\">" + roles[num] + "</td>"]
        for each_zone in zones:
            progress = data[each_zone]
            image = "\n".join(["<img src=\"" + build_path(ASSETS, ["image", "jx3", "cat", "gold.png" if not value else "grey.png"]) + "\" height=\"20\" width=\"20\">" for value in progress])
            row.append("<td class=\"short-column\">" + image + "</td>")
        tables.append(
            "<tr>\n" + "\n".join(row) + "\n</tr>"
        )
        num += 1
    html = str(
            HTMLSourceCode(
                application_name = f" · 副本记录 · {server} · " + "+".join(roles),
                table_head = table_head,
                table_body = "\n".join(tables)
            )
        )
    image = await generate(html, "table", segment=True)
    return image

async def get_personal_roles_teamcd_image(user_id: int):
    personal_settings: PersonalSettings | Any = db.where_one(PersonalSettings(), "user_id = ?", str(user_id), default=None)
    if personal_settings is None:
        return "您尚未绑定任何角色！请绑定后再尝试查询！"
    roles = sort_role_daa(personal_settings.roles)
    responses = [
        (await request.post(tuilan=True)).json()
        for request
        in [
            build_teamcd_request(r.globalRoleId)
            for r
            in roles
        ]
    ]
    roles_data: list[list[dict[str, list[bool]]]] = [[] for _ in range(len(roles))]
    num = 0
    for each_response in responses:
        roles_data[num].append(parse_data(each_response))
        num += 1
    final_data = synchronize_keys(roles_data)
    zones: list[str] = list(set(chain.from_iterable(d.keys() for sublist in final_data for d in sublist)))
    table_head = "<tr><th class=\"short-column\">服务器</th><th class=\"short-column\">角色</th><th class=\"short-column\">门派</th>" + "\n".join([f"<th class=\"short-column\">{zone}</th>" for zone in zones]) + "</tr>"
    tables: list[str] = []
    num = 0
    for each_role_data in roles_data:
        data = each_role_data[0]
        row = ["<td class=\"short-column\" style=\"color:" + (School(roles[num].forceName).color or "") + "\">" + roles[num].serverName + "</td><td class=\"short-column\" style=\"color:" + (School(roles[num].forceName).color or "") + "\">" + roles[num].roleName + "<td class=\"short-column\" style=\"color:" + (School(roles[num].forceName).color or "") + "\">" + roles[num].forceName + "</td></td>"]
        for each_zone in zones:
            progress = data[each_zone]
            image = "\n".join(["<img src=\"" + build_path(ASSETS, ["image", "jx3", "cat", "gold.png" if not value else "grey.png"]) + "\" height=\"20\" width=\"20\">" for value in progress])
            row.append("<td class=\"short-column\">" + image + "</td>")
        tables.append(
            "<tr>\n" + "\n".join(row) + "\n</tr>"
        )
        num += 1
    html = str(
            HTMLSourceCode(
                application_name = " · 所有角色副本记录 ",
                table_head = table_head,
                table_body = "\n".join(tables),
                additional_css = Path(TEMPLATES + "/jx3/teamcd.css").as_uri()
            )
        )
    image = await generate(html, "table", segment=True)
    return image