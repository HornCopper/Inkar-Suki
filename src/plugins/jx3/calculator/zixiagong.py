# DPS计算器 紫霞功

from typing import Tuple, Literal, Optional, List, Union, Dict, Callable
from jinja2 import Template
from pathlib import Path

from src.constant.jx3 import color_list

from src.tools.basic.server import Zone_mapping, server_mapping
from src.tools.utils.request import get_api, post_url
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.utils.file import read, write
from src.tools.generate import generate, get_uuid
from src.tools.basic.prompts import PROMPT
from src.tools.config import Config

from src.plugins.jx3.detail.detail import get_tuilan_data
from src.plugins.jx3.bind.role import get_player_local_data
from src.plugins.jx3.attributes.api import get_personal_kf, enchant_mapping

import json

inkarsuki_offical_token = Config.hidden.offcial_token

msgbox_dujing = """
<div class="element">
    <div class="cell-title"><span>理论DPS</span></div>
    <div class="cell">{{ max }}</div>
</div>
<div class="element">
    <div class="cell-title"><span>脸黑DPS</span></div>
    <div class="cell">{{ min }}</div>
</div>"""

template_calculator_dujing = """
<tr>
    <td class="short-column">{{ skill }}</td>
    <td class="short-column">
        <div class="progress-bar" style="margin: 0 auto;">
            <div class="progress" style="width: {{ display }};"></div>
            <span class="progress-text">{{ percent }}</span>
        </div>
    </td>
    <td class="short-column">{{ count }}</td>
    <td class="short-column">{{ value }}</td>
</tr>"""

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
                    enchant_name = enchant_mapping(equip["Quality"])
                    if not isinstance(enchant_name, str):
                        raise ValueError("Unknown enchant of \"" + equip["Name"] + "(" + equip["Quality"] + ")`.")
                    return self.enchant_map[enchant_name]
        return "无"
    
    @property
    def is_shoe_enchant(self) -> str:
        for equip in self.data["Equips"]:
            if equip["Icon"]["SubKind"] == "鞋":
                if "WPermanentEnchant" in equip:
                    enchant_name = enchant_mapping(equip["Quality"])
                    if not isinstance(enchant_name, str):
                        raise ValueError("Unknown enchant of \"" + equip["Name"] + "(" + equip["Quality"] + ")`.")
                    return self.enchant_map[enchant_name]
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
                        result.append(attr_data["value"])
        return result
            
    
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
    
async def get_calculated_img_zixiagong(server: Optional[str], name: str, group_id: Optional[str]):
    server_ = server_mapping(server, group_id)
    if not server_:
        return [PROMPT.ServerNotExist]
    player_data = await get_player_local_data(role_name=name, server_name=server_)
    if player_data.format_jx3api()["code"] != 200:
        return [PROMPT.PlayerNotExist]
    params = {
        "zone": Zone_mapping(server_),
        "server": server_,
        "game_role_id": player_data.format_jx3api()["data"]["roleId"]
    }
    tuilan_data = await get_tuilan_data("https://m.pvp.xoyo.com/mine/equip/get-role-equip", params=params)
    school = await get_personal_kf(tuilan_data["data"]["Kungfu"]["KungfuID"])
    if school != "紫霞功":
        return ["唔……门派与计算器不匹配！"]
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
        "qixue": qixue
    }
    calculated_data = await post_url("http://117.50.178.116:2333/calculator_zxg", json=params, headers={"token": inkarsuki_offical_token}, timeout=10000)
    calculated_data = json.loads(calculated_data)
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
            Template(template_calculator_dujing).render(**{
                "skill": skill["skill"],
                "display": str(round(skill["damage"]/final_data[0]["damage"]*100, 2)) + "%",
                "percent": skill["percent"],
                "count": str(skill["count"]),
                "value": str(skill["damage"])
            })
        )
    html = Template(read(VIEWS + "/jx3/calculator/calculator.html")).render(**{
        "font": ASSETS + "/font/custom.ttf",
        "yozai": ASSETS + "/font/Yozai-Medium.ttf",
        "msgbox": Template(msgbox_dujing).render(**{
            "max": dps,
            "min": bad_dps
        }),
        "tables": "\n".join(tables),
        "school": "紫霞功",
        "color": color_list["紫霞功"],
        "server": server,
        "name": name,
        "calculator": "【雾海寻龙】气纯dps计算器 v1.247(240912) by @月慕青尘"
    })
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()