# DPS计算器 毒经

from typing import List, Literal
from jinja2 import Template
from pathlib import Path
from pydantic import BaseModel

from src.utils.network import Request
from src.const.jx3.server import Server
from src.const.jx3.kungfu import Kungfu
from src.const.prompts import PROMPT
from src.templates import SimpleHTML
from src.const.path import ASSETS, CACHE, build_path
from src.utils.generate import get_uuid, generate
from src.config import Config

from src.utils.database.player import search_player

from ._template import template_calculator_dujing, msgbox_dujing

import json

inkarsuki_offical_token = Config.hidden.offcial_token

class ExcelRequest(BaseModel):
    attrs: List[int | str]
    weapon: Literal["", "墨语沉香", "13950水特效", "龙门飞剑", "小橙武特效"]
    sash: Literal["", "秋风韵"]
    enchant: List[bool]
    suit: List[bool]
    qixue: Literal["曲致", "固灵"]

async def get_calculated_data(
    attrs: List[int | str],
    weapon: Literal["", "墨语沉香", "13950水特效", "龙门飞剑", "小橙武特效"],
    sash: Literal["", "秋风韵"],
    enchant: List[bool],
    suit: List[bool],
    qixue: Literal["曲致", "固灵"]
) -> dict:
    params = {
        "attrs": attrs,
        "weapon": weapon,
        "sash": sash,
        "enchant": enchant,
        "suit": suit,
        "qixue": qixue
    }
    data = (await Request("http://206.237.21.122:25765/calculator_dj", params=params, headers={"token": inkarsuki_offical_token}).post(timeout=12000)).json()
    return data

def check_set_effects(equip_list):
    skill_event_handler_activated = False
    set_equipment_recipe_activated = False

    for equip in equip_list:
        if "SetListMap" in equip and "Set" in equip:
            equipped_set_pieces = len(equip["SetListMap"])

            for effect in equip["Set"]:
                set_num = int(effect.get("SetNum", 0))

                if effect["Desc"] == "atSkillEventHandler" and equipped_set_pieces >= set_num:
                    skill_event_handler_activated = True

                if effect["Desc"] == "atSetEquipmentRecipe" and equipped_set_pieces >= set_num:
                    set_equipment_recipe_activated = True

    return [skill_event_handler_activated, set_equipment_recipe_activated]

def get_key_qixue(qixue_list: list):
    for qx in qixue_list:
        if qx["name"] == "固灵":
            return "固灵"
    return "曲致"

async def analyze_attrs(attrs_raw_data: dict) -> ExcelRequest:
    weapon = ""
    sash = ""
    enchant = []
    suit = []
    for equip in attrs_raw_data["data"]["Equips"]:
        if equip["Icon"]["Kind"] == "武器" and equip["Icon"]["SubKind"] != "投掷囊":
            if (equip["Name"], equip["Quality"]) == ("十方断魂笛·虫魂", "13200"):
                weapon = "龙门飞剑"
            if (equip["Name"], equip["Quality"]) == ("墨语沉香", "12500"):
                weapon = "墨语沉香"
            if equip["Name"] == "悠哉乐土":
                weapon = "13950水特效"
            if (equip["Name"], equip["Quality"]) == ("死生往复·牵丝", "11650"):
                weapon = "小橙武特效"
        if equip["Icon"]["SubKind"] == "腰坠":
            if equip["Name"] == "秋风韵":
                sash = "秋风韵"
    for place in ["帽子", "上衣", "腰带", "护臂", "鞋"]:
        flag = False
        for equip in attrs_raw_data["data"]["Equips"]:
            if equip["Icon"]["SubKind"] == place:
                if "WPermanentEnchant" in equip:
                    enchant.append(True)
                    flag = True
                else:
                    enchant.append(False)
                    flag = True
        if not flag:
            enchant.append(False)
    suit = check_set_effects(attrs_raw_data["data"]["Equips"])
    panel = attrs_raw_data["data"]["PersonalPanel"]
    attrs = []
    for attr_name in ["根骨", "攻击力", "会心", "会心效果", "破防", "破招", "无双", "加速"]:
        for attr_data in panel:
            if attr_data["name"] == attr_name:
                if attr_data["percent"] and attr_name != "加速":
                    attrs.append(str(attr_data["value"]) + "%")
                if not attr_data["percent"] and attr_name != "加速":
                    attrs.append(attr_data["value"])
                if attr_name == "加速":
                    attrs.append("%.2f%%" % (attr_data["value"]/96483.75 * 100))
    return ExcelRequest(
        attrs=attrs,
        weapon=weapon,
        sash=sash,
        enchant=enchant,
        suit=suit,
        qixue=get_key_qixue(attrs_raw_data["data"]["Person"]["qixueList"])
    )

async def generate_calculator_img_dujing(server: str, name: str):
    role_data = await search_player(role_name=name, server_name=server)
    if role_data.format_jx3api()["code"] != 200:
        return [PROMPT.PlayerNotExist]
    uid = role_data.format_jx3api()["data"]["roleId"]
    params = {
        "zone": Server(server).zone,
        "server": server,
        "game_role_id": uid
    }
    equip_data = (await Request("https://m.pvp.xoyo.com/mine/equip/get-role-equip", params=params).post(tuilan=True)).json()
    kungfu = Kungfu.with_internel_id(equip_data["data"]["Kungfu"]["KungfuID"])
    if kungfu.name != "毒经":
        return [PROMPT.CalculatorNotMatch]
    analyzed_data: ExcelRequest = await analyze_attrs(equip_data)
    calculated_data = await get_calculated_data(**(analyzed_data.__dict__))
    tables = []
    max_dps = calculated_data["data"]["result"] # 手打
    min_dps = int(max_dps*0.985) # 一键宏
    for skill_sort in range(len(calculated_data["data"]["skills"])):
        tables.append(
            Template(template_calculator_dujing).render(**{
                "skill": calculated_data["data"]["skills"][skill_sort],
                "display": str(int(round(float(calculated_data["data"]["percent"][skill_sort][:-1])/float(calculated_data["data"]["percent"][0][:-1]), 2)*100)) + "%",
                "percent": calculated_data["data"]["percent"][skill_sort],
                "count": str(calculated_data["data"]["counts"][skill_sort]) + "（" + calculated_data["data"]["critical"][skill_sort] + "会心）",
                "value": calculated_data["data"]["damages"][skill_sort]
            })
        )
    html = str(
        SimpleHTML(
            html_type = "jx3",
            html_template = "calculator",
            **{
                "font": build_path(ASSETS, ["font", "custom.ttf"]),
                "yozai": build_path(ASSETS, ["font", "Yozai-Medium.ttf"]),
                "msgbox": Template(msgbox_dujing).render(**{
                    "max": max_dps,
                    "min": min_dps
                }),
                "tables": "\n".join(tables),
                "school": "毒经",
                "color": Kungfu("毒经").color,
                "server": server,
                "name": name,
                "calculator": "【雾海寻龙】毒经DPS计算器 240806"
            }
        )
    )
    final_path = await generate(html, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()