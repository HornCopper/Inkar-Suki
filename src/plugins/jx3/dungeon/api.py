from pathlib import Path
from nonebot.log import logger
from jinja2 import Template

from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.database.player import search_player
from src.utils.tuilan import gen_ts, dungeon_sign
from src.utils.time import Time
from src.templates import HTMLSourceCode

import json
import re
import time

from ._template import (
    star, 
    template_drop, 
    table_drop_head,
    image_template,
    template_zone_record,
    table_zone_record_head,
    template_item,
    table_item_head
)

async def get_map(name: str, mode: str) -> int | None:
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


async def get_boss(map: str, mode: str, boss: str) -> str | None:
    map_id = await get_map(map, mode)
    params = {
        "map_id": map_id
    }
    data = (await Request(url="https://m.pvp.xoyo.com/dungeon/info", params=params).post(tuilan=True)).json()
    for i in data["data"]["info"]["boss_infos"]:
        if i["name"] == boss:
            return i["index"]


async def get_drops(map: str, mode: str, boss: str) -> dict:
    boss_id = await get_boss(map, mode, boss)
    params = {
        "boss_id": boss_id
    }
    data = (await Request(url="https://m.pvp.xoyo.com/dungeon/boss-drop", params=params).post(tuilan=True)).json()
    return data

# 暂时不打算做5人副本，5人副本与10人副本的请求地址不同。
# 10人/25人：https://m.pvp.xoyo.com/dungeon/list
# 5人：https://m.pvp.xoyo.com/dungeon/list-all
# 暂时未知数据是否相同，后续考虑是否添加。

equip_types = ["帽子", "上衣", "腰带", "护臂", "裤子", "鞋", "项链", "腰坠", "戒指", "投掷囊"]

filter_words = ["根骨", "力道", "元气", "身法", "体质"]

async def get_drop_list_image(map: str, mode: str, boss: str):
    try:
        data = await get_drops(map, mode, boss)
    except KeyError:
        return ["唔……没有找到该掉落列表，请检查副本名称、BOSS名称或难度~"]
    data = data["data"]
    armors = data["armors"]
    others = data["others"]
    weapons = data["weapons"]
    if armors is None:
        armors = []
    if others is None:
        others = []
    if weapons is None:
        weapons = []
    if len(armors) == 0 and len(others) == 0 and len(weapons) == 0:
        return ["唔……没有找到该boss的掉落哦~\n您确定" + f"{boss}住在{mode}{map}吗？"]
    else:
        table_content = []
        for i in armors:
            name = i["Name"]
            icon = i["Icon"]["FileName"]
            if i["Icon"]["SubKind"] in equip_types:
                if "Type" in list(i):
                    if i["Type"] == "Act_运营及版本道具":
                        type_ = "外观"
                        attrs = "不适用"
                        fivestone = "不适用"
                        max = "不适用"
                        quailty = "不适用"
                        score = "不适用"
                        type_ = "装备"
                    else:
                        type_ = re.sub(r"\d+", "", i["Icon"]["SubKind"])
                        attrs = "不适用"
                        fivestone = "不适用"
                        max = "不适用"
                        quailty = "不适用"
                        score = "不适用"
                else:
                    type_ = i["Icon"]["SubKind"]
                    attrs_data = i["ModifyType"]
                    attrs_list = []
                    for x in attrs_data:
                        string = x["Attrib"]["GeneratedMagic"]
                        flag = False
                        for y in filter_words:
                            if string.find(y) != -1:
                                flag = True
                        if flag:
                            continue
                        attrs_list.append(string)
                    attrs = "<br>".join(attrs_list)
                    if i["Icon"]["SubKind"] != "戒指":
                        diamon_data = i["DiamonAttribute"]
                        diamon_list = []
                        for x in diamon_data:
                            if x["Desc"] == "atInvalid":
                                continue
                            diamon_string = re.sub(r"\d+", "?", x["Attrib"]["GeneratedMagic"])
                            diamon_list.append(diamon_string)
                        fivestone = "<br>".join(diamon_list)
                    else:
                        fivestone = "不适用"
                    max = i["MaxStrengthLevel"]
                    stars = []
                    if max != "":
                        for x in range(int(max)):
                            stars.append(star)
                        stars = "\n".join(stars)
                    else:
                        stars = "<p>不适用</p>"
                    quailty = i["Quality"]
                    equip_type = i["Icon"]["SubKind"]
                    if equip_type == "帽子":
                        score = str(int(int(quailty)*1.62))
                    elif equip_type in ["上衣", "裤子"]:
                        score = str(int(int(quailty)*1.8))
                    elif equip_type in ["腰带", "护臂", "鞋"]:
                        score = str(int(int(quailty)*1.26))
                    elif equip_type in ["项链", "腰坠", "戒指"]:
                        score = str(int(int(quailty)*0.9))
                    elif equip_type in ["投掷囊"]:
                        score = str(int(int(quailty)*1.08))
            else:
                type_ = "未知"
                flag = False
                if "Type" in list(i):
                    if i["Type"] == "Act_运营及版本道具":
                        type_ = "外观"
                        flag = True
                if flag is False:
                    type_ = re.sub(r"\d+", "", i["Icon"]["SubKind"])
                attrs = "不适用"
                fivestone = "不适用"
                stars = "不适用"
                quailty = "不适用"
                score = "不适用"
            table_content.append(
                Template(template_drop).render(
                    icon = icon,
                    name = name,
                    attrs = attrs,
                    type = type_,
                    stars = stars,
                    quality = quailty,
                    score = score,
                    fivestone = fivestone
                )
            )
        for i in weapons:
            name = i["Name"]
            icon = i["Icon"]["FileName"]
            type_ = i["Icon"]["SubKind"] if i["Icon"]["SubKind"] != "投掷囊" else "暗器"
            attrs_data = i["ModifyType"]
            attrs_list = []
            for x in attrs_data:
                string = x["Attrib"]["GeneratedMagic"]
                flag = False
                for y in filter_words:
                    if string.find(y) != -1:
                        flag = True
                if flag:
                    continue
                attrs_list.append(string)
            attrs = "<br>".join(attrs_list)
            diamon_data = i["DiamonAttribute"]
            diamon_list = []
            for x in diamon_data:
                if x["Desc"] == "atInvalid":
                    continue
                string = re.sub(r"\d+", "?", x["Attrib"]["GeneratedMagic"])
                diamon_list.append(string)
            fivestone = "<br>".join(diamon_list)
            max = i["MaxStrengthLevel"]
            stars = []
            if max != "":
                for x in range(int(max)):
                    stars.append(star)
                stars = "\n".join(stars)
            else:
                stars = "<p>不适用</p>"
            quailty = i["Quality"]
            score = str(int(int(quailty)*2.16))
            Template(template_drop).render(
                icon = icon,
                name = name,
                attrs = attrs,
                type = type_,
                stars = stars,
                quality = quailty,
                score = score,
                fivestone = fivestone
            )
        for i in others:
            type_ = "不适用"
            icon = i["Icon"]["FileName"]
            name = i["Name"]
            attrs = "不适用"
            stars = "不适用"
            score = "不适用"
            quailty = "不适用"
            fivestone = "不适用"
            table_content.append(
                Template(template_drop).render(
                    icon = icon,
                    name = name,
                    attrs = attrs,
                    type = type_,
                    stars = stars,
                    quality = quailty,
                    score = score,
                    fivestone = fivestone
                )
            )
        html = str(
            HTMLSourceCode(
                application_name = f" · 掉落列表 · {mode}{map} · {boss}",
                additional_css = Path(build_path(TEMPLATES, ["jx3", "drop.css"])).as_uri(),
                table_head = table_drop_head,
                table_body = "\n".join(table_content)
            )
        )
        final_path = await generate(html, "table", False, 500)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()

async def get_zone_record_image(server: str, role: str):
    data = await search_player(role_name=role, server_name=server)
    details_data = data.format_jx3api()
    if details_data["code"] != 200:
        guid = ""
        return ["唔……获取玩家信息失败。"]
    else:
        guid = details_data["data"]["globalRoleId"]
    ts = gen_ts()
    params = {
        "globalRoleId": guid,
        "sign": dungeon_sign(f"globalRoleId={guid}&ts={ts}"),
        "ts": ts
    }
    data = (await Request("https://m.pvp.xoyo.com/h5/parser/cd-process/get-by-role", params=params).post(tuilan=True)).json()
    unable = Template(image_template).render(
        image_path = build_path(ASSETS, ["image", "jx3", "cat", "grey.png"])
    )
    available = Template(image_template).render(
        image_path = build_path(ASSETS, ["image", "jx3", "cat", "gold.png"])
    )
    if data["data"] == []:
        return ["该玩家目前尚未打过任何副本哦~\n注意：10人普通副本会在周五刷新一次。"]
    else:
        contents = []
        if data is None:
            return ["获取玩家信息失败！"]
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
        final_path = await generate(html, "table", False)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()