from pathlib import Path
from jinja2 import Template

from src.const.path import TEMPLATES, build_path
from src.utils.network import Request
from src.utils.generate import generate

from src.templates import HTMLSourceCode

from src.plugins.jx3.joy.random_item import item_colors as COLOR

import re

from ._template import (
    star, 
    template_drop, 
    table_drop_head
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

def parse_attr(data: dict) -> str:
    msg = ""
    if "ModifyType" not in data:
        return ""
    for i in data["ModifyType"]:
        content = i["Attrib"]["GeneratedMagic"].split("提高")
        if len(content) == 1:
            content = content[0].split("增加")
        attr = content[0]
        attr = attr.replace("外功防御", "外防")
        attr = attr.replace("内功防御", "内防")
        attr = attr.replace("会心效果", "会效")
        filter_string = ["全", "阴性", "阳性", "阴阳", "毒性", "值", "成效", "体质", "等级", "混元性", "招式产生威胁", "水下呼吸时间", "抗摔系数", "马术气力上限", "气力上限"]
        for y in filter_string:
            attr = attr.replace(y, "")
        if attr != "" and len(attr) <= 4:
            msg = msg + f" {attr}"
    msg = msg.replace(" 能 ", " 全能 ").replace(" 能", " 全能")
    return msg.strip()

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
        return "唔……没有找到该掉落列表，请检查副本名称、BOSS名称或难度~"
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
        return "唔……没有找到该boss的掉落哦~\n您确定" + f"{boss}住在{mode}{map}吗？"
    else:
        table_content = []
        for i in armors:
            name = i["Name"]
            icon = i["Icon"]["FileName"]
            color = COLOR[int(i["Color"]) if "Color" in i else 4]
            if i["Icon"]["SubKind"] in equip_types:
                if "Type" in i:
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
                    attrs_data = i
                    attrs = parse_attr(attrs_data)
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
                color = COLOR[int(i["Color"]) if "Color" in i else 4]
                if str(name).endswith("玄晶"):
                    color = COLOR[5]
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
                    color = color,
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
            attrs_data = i
            attrs = parse_attr(attrs_data)
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
                color = COLOR[int(i["Color"]) if "Color" in i else 4],
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
            color = COLOR[int(i["Color"]) if "Color" in i else 4]
            if str(name).endswith("玄晶"):
                color = COLOR[5]
            attrs = "不适用"
            stars = "不适用"
            score = "不适用"
            quailty = "不适用"
            fivestone = "不适用"
            table_content.append(
                Template(template_drop).render(
                    icon = icon,
                    name = name,
                    color = color,
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
                application_name = f"掉落列表 · {mode}{map} · {boss}",
                additional_css = Path(build_path(TEMPLATES, ["jx3", "drop.css"])).as_uri(),
                table_head = table_drop_head,
                table_body = "\n".join(table_content)
            )
        )
        image = await generate(html, ".container", False, 500, segment=True)
        return image