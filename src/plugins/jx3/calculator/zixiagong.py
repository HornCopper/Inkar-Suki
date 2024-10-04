# DPS计算器 紫霞功

from typing import Tuple, List
from jinja2 import Template
from pathlib import Path

from src.config import Config
from src.const.jx3.server import Server
from src.const.jx3.kungfu import Kungfu
from src.const.prompts import PROMPT
from src.const.path import ASSETS, build_path
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.database.player import search_player
from src.templates import SimpleHTML

from src.plugins.jx3.attributes.v2 import Enchant

import json

from ._template import msgbox_zixiagong, template_calculator_zixiagong

inkarsuki_offical_token = Config.hidden.offcial_token


def process_skill_data(skills, counts, damages, percent):
    combined_list = [
        {
            "skill": skill,
            "count": count,
            "damage": damage,
            "percent": percent
        }
        for skill, count, damage, percent in zip(skills, counts, damages, percent)
    ]

    filtered_list = [item for item in combined_list if item["damage"] > 0]
    sorted_list = sorted(filtered_list, key=lambda x: x["damage"], reverse=True)
    return sorted_list

class ZiXiaGongAttributes:
    enchant_map = {
        "天堑奇珵": "15400",
        "天堑奇玿": "13950",
        "天堑奇瑛": "12450"
    }

    def __init__(self, data: dict):
        self.data = data["data"]

    @property
    def is_xcw(self) -> bool:
        for equip in self.data["Equips"]:
            if equip["Name"] == "愧琼瑰·珠沉" and equip["Quality"] in ["11650", "10900"]:
                return True
        return False

    @property
    def is_dcw(self) -> bool:
        for equip in self.data["Equips"]:
            if equip["Name"] == "苍冥游" and equip["Quality"] != "1":
                return True
        return False
    
    @property
    def is_belt_enchant(self) -> bool:
        for equip in self.data["Equips"]:
            if equip["Icon"]["SubKind"] == "腰带":
                if "WPermanentEnchant" in equip:
                    return True
        return False
    
    @property
    def is_wristband_enchant(self) -> str:
        for equip in self.data["Equips"]:
            if equip["Icon"]["SubKind"] == "护臂":
                if "WPermanentEnchant" in equip:
                    enchant_name = Enchant(equip["Quality"]).name
                    if not isinstance(enchant_name, str):
                        raise ValueError("Unknown enchant of \"" + equip["Name"] + "(" + equip["Quality"] + ")`.")
                    return self.enchant_map[enchant_name] + "护腕大附魔"
        return "无"
    
    @property
    def is_shoe_enchant(self) -> str:
        for equip in self.data["Equips"]:
            if equip["Icon"]["SubKind"] == "鞋":
                if "WPermanentEnchant" in equip:
                    enchant_name = Enchant(equip["Quality"]).name
                    if not isinstance(enchant_name, str):
                        raise ValueError("Unknown enchant of \"" + equip["Name"] + "(" + equip["Quality"] + ")`.")
                    return self.enchant_map[enchant_name] + "鞋子大附魔"
        return "无"
    
    @property
    def is_special_weapon(self) -> str:
        for equip in self.data["Equips"]:
            if equip["Name"] in ["仙家楼阁", "伴雪声", "岁载空"]:
                return "水特效·" + equip["Quality"]
        return "无"
    
    @property
    def is_special_sash(self) -> str:
        for equip in self.data["Equips"]:
            if equip["Name"] in ["暮天阳", "池上雨", "秋风韵"]:
                return equip["Name"] + "·" + equip["Quality"]
        return "无"
    
    @property
    def attributes(self) -> List[str]:
        result = []
        for attr_type in ["基础攻击力", "攻击力", "会心", "会心效果", "破防", "无双", "破招"]:
            for attr_data in self.data["PersonalPanel"]:
                if attr_data["name"] == attr_type:
                    if attr_data["percent"]:
                        result.append(str(attr_data["value"]) + "%")
                    else:
                        result.append(str(attr_data["value"]))
        return result
    
    @property
    def mode(self) -> str:
        dcw = self.is_dcw
        xcw = self.is_xcw
        speed = 0
        for attr_data in self.data["PersonalPanel"]:
            if attr_data["name"] == "加速":
                speed = attr_data["value"]
        if not dcw and not xcw:
            return "紫武技能数标准模式"
        if dcw:
            if speed >= 4241:
                return "橙武二段加速技能标准值"
            if speed >= 95:
                return "橙武一段加速技能标准值"
        if xcw:
            if speed >= 4241:
                return "小橙武二段技能数标准值"
        return "紫武技能数标准模式"
            
            
    
    @property
    def check_set_effects(self) -> Tuple[bool, bool]:
        attr_event = False
        damage_event = False
        for equip in self.data["Equips"]:
            if "SetListMap" in equip and "Set" in equip:
                set_count = len(equip["SetListMap"])
                for effect in equip["Set"]:
                    set_num = int(effect.get("SetNum", 0))
                    if effect["Desc"] == "atSkillEventHandler" and set_count >= set_num:
                        attr_event = True
                    if effect["Desc"] == "atSetEquipmentRecipe" and set_count >= set_num:
                        damage_event = True
        return attr_event, damage_event
    
    def check_qixue(self, name: str) -> bool:
        for qixue in self.data["Person"]["qixueList"]:
            if qixue["name"] == name:
                return True
        return False
    
async def get_calculated_img_zixiagong(server: str, name: str):
    player_data = await search_player(role_name=name, server_name=server)
    if player_data.format_jx3api()["code"] != 200:
        return [PROMPT.PlayerNotExist]
    params = {
        "zone": Server(server).zone,
        "server": server,
        "game_role_id": player_data.format_jx3api()["data"]["roleId"]
    }
    tuilan_data = (await Request("https://m.pvp.xoyo.com/mine/equip/get-role-equip", params=params).post(tuilan=True)).json()
    school = Kungfu.with_internel_id(tuilan_data["data"]["Kungfu"]["KungfuID"])
    if school.name != "紫霞功":
        return [PROMPT.CalculatorNotMatch]
    data_obj = ZiXiaGongAttributes(tuilan_data)
    attrs = data_obj.attributes
    cw = [data_obj.is_dcw, data_obj.is_xcw]
    suit = list(data_obj.check_set_effects)
    belt = "无"
    if data_obj.is_belt_enchant:
        belt = "全等级腰带大附魔"
    enchant = [belt, data_obj.is_wristband_enchant, data_obj.is_shoe_enchant]
    sash = data_obj.is_special_sash
    weapon = data_obj.is_special_weapon
    mode = data_obj.mode
    qixue: List[bool] = []
    for qixue_name in ["万物", "正气", "破势", "抱阳", "若冲"]:
        qixue.append(data_obj.check_qixue(qixue_name))
    params = {
        "attrs": attrs,
        "cw": cw,
        "suit": suit,
        "enchant": enchant,
        "sash": sash,
        "weapon": weapon,
        "qixue": qixue,
        "mode": mode
    }
    calculated_data = (await Request("http://206.237.21.122:25765/calculator_zxg", params=params, headers={"token": inkarsuki_offical_token}).post(timeout=10000)).json()
    dps = calculated_data["data"]["result"]
    bad_dps = calculated_data["data"]["bad_result"]
    final_data = process_skill_data(
        skills=calculated_data["data"]["skills"],
        counts=calculated_data["data"]["counts"],
        damages=calculated_data["data"]["damages"],
        percent=calculated_data["data"]["percent"]
    )
    tables = []
    for skill in final_data:
        tables.append(
            Template(template_calculator_zixiagong).render(**{
                "skill": skill["skill"],
                "display": str(round(skill["damage"]/final_data[0]["damage"]*100, 2)) + "%",
                "percent": skill["percent"],
                "count": str(skill["count"]),
                "value": str(skill["damage"])
            })
        )
    html = str(
        SimpleHTML(
            html_type = "jx3",
            html_template = "calculator",
            **{
                "font": build_path(ASSETS, ["font", "custom.ttf"]),
                "yozai": build_path(ASSETS, ["font", "Yozai-Medium.ttf"]),
                "msgbox": Template(msgbox_zixiagong).render(**{
                    "max": dps,
                    "min": bad_dps
                }),
                "tables": "\n".join(tables),
                "school": "紫霞功",
                "color": Kungfu("紫霞功").color,
                "server": server,
                "name": name,
                "calculator": "【雾海寻龙】气纯dps计算器 v1.247(240912) by @月慕青尘"
            }
        )
    )
    final_path = await generate(html, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()