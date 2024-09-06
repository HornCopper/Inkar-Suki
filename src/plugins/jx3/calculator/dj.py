# DPS计算器 毒经

from typing import List, Union, Literal, Optional
from jinja2 import Template
from pathlib import Path
from pydantic import BaseModel

from src.constant.jx3 import color_list

from src.tools.utils.request import post_url
from src.tools.basic.server import server_mapping, Zone_mapping
from src.tools.basic.prompts import PROMPT
from src.tools.basic.jx3 import gen_ts
from src.tools.utils.file import read, write
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.generate import get_uuid, generate
from src.tools.config import Config

from src.plugins.jx3.bind.role import get_player_local_data
from src.plugins.jx3.detail.detail import get_tuilan_data
from src.plugins.jx3.attributes.api import get_personal_kf

import json

inkarsuki_offical_token = Config.hidden.offcial_token

msgbox_dujing = """
<div class="element">
    <div class="cell-title"><span>手打</span></div>
    <div class="cell">{{ max }}</div>
</div>
<div class="element">
    <div class="cell-title"><span>一键宏</span></div>
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

class ExcelRequest(BaseModel):
    attrs: List[Union[int, str]]
    weapon: Literal["", "墨语沉香", "13950水特效", "龙门飞剑", "小橙武特效"]
    sash: Literal["", "秋风韵"]
    enchant: List[bool]
    suit: List[bool]
    qixue: Literal["曲致", "固灵"]

async def get_calculated_data(
    attrs: List[Union[int, str]],
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
    data = await post_url(
        url = "http://117.50.178.116:2333/calculator",
        json = params,
        headers = {
            "token": inkarsuki_offical_token
        },
        timeout=10000
    )
    return json.loads(data)

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
        if qx["name"] == "曲致":
            return "曲致"
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
            if equip["Name"] == "十方断魂笛·虫魂" and equip["Quality"] == "13200":
                weapon = "龙门飞剑"
            if equip["Name"] == "墨语沉香" and equip["Quality"] == "12500":
                weapon = "墨语沉香"
            if equip["Name"] == "悠哉乐土":
                weapon = "13950水特效"
            if equip["Name"] == "死生往复·牵丝" and equip["Quality"] == "11650":
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

async def generate_calculator_img_dujing(server: Optional[str], name: str, group_id: str = ""):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    role_data = await get_player_local_data(role_name=name, server_name=server)
    if role_data.format_jx3api()["code"] != 200:
        return [PROMPT.PlayerNotExist]
    uid = role_data.format_jx3api()["data"]["roleId"]
    param = {
        "zone": Zone_mapping(server),
        "server": server,
        "game_role_id": uid,
        "ts": gen_ts()
    }
    equip_data = await get_tuilan_data("https://m.pvp.xoyo.com/mine/equip/get-role-equip", param)
    kungfu = await get_personal_kf(equip_data["data"]["Kungfu"]["KungfuID"])
    if kungfu != "毒经":
        return ["唔……门派与计算器不匹配！"]
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
    html = Template(read(VIEWS + "/jx3/calculator/calculator.html")).render(**{
        "font": ASSETS + "/font/custom.ttf",
        "yozai": ASSETS + "/font/Yozai-Medium.ttf",
        "msgbox": Template(msgbox_dujing).render(**{
            "max": max_dps,
            "min": min_dps
        }),
        "tables": "\n".join(tables),
        "school": "毒经",
        "color": color_list["毒经"],
        "server": server,
        "name": name,
        "calculator": "【雾海寻龙】毒经DPS计算器 240806"
    })
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()