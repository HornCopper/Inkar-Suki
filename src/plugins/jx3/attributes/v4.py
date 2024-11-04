from pathlib import Path
from jinja2 import Environment, DebugUndefined, Template

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.const.jx3.kungfu import Kungfu
from src.const.path import (
    ASSETS,
    build_path
)
from src.templates import SimpleHTML
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.database.player import search_player

from .v2 import Qixue, Enchant
from ._template import template_attrs_v4

import json

async def get_basic_info(server: str, name: str):
    data = await search_player(role_name=name, server_name=server)
    data = data.format_jx3api()
    if data["code"] != 200:
        return 404
    else:
        data = data["data"]
        tuilan_status = "已绑定" if data.get("personId") != "" else "未绑定"
        return [data.get("roleName"), str(data.get("roleId")), data.get("tongName"), data.get("forceName"), data.get("bodyName"), data.get("campName"), tuilan_status]
    
def location_mapping(location: str):
    return {
        "帽子": "帽",
        "上衣": "衣",
        "腰带": "腰",
        "护臂": "腕",
        "鞋": "鞋"
    }[location]

def get_equip_attr(data: list, role_type: str):
    msg = ""
    for i in data:
        content = i["Attrib"]["GeneratedMagic"].split("提高")
        if len(content) == 1:
            content = content[0].split("增加")
        attr = content[0]
        attr = attr.replace("外功防御", "外防")
        attr = attr.replace("内功防御", "内防")
        attr = attr.replace("会心效果", "会效")
        filter_string = ["全", "阴性", "阳性", "阴阳", "毒性", "攻击", "值", "成效", "内功", "外功", "体质", "根骨", "力道", "元气", "身法", "等级", "混元性", "招式产生威胁", "水下呼吸时间", "抗摔系数", "马术气力上限"]
        for y in filter_string:
            if attr == "全能":
                continue
            attr = attr.replace(y, "")
        if attr != "":
            if role_type == "防御":
                msg = msg + f" {attr[0]}"
            else:
                msg = msg + f" {attr}"
    return msg

async def get_attrs_v4(server: str, name: str):
    basic_info = await get_basic_info(server, name)
    if basic_info == 404:
        return [PROMPT.PlayerNotExist]
    params = {
        "zone": Server(server).zone,
        "server": server,
        "game_role_id": basic_info[1],
    }
    data = (await Request(url="https://m.pvp.xoyo.com/mine/equip/get-role-equip", params=params).post(tuilan=True)).json()
    basic_info_key = ["角色名", "UID", "帮会", "门派", "体型", "阵营", "推栏", "装分", "气血"]
    basic_info.append(data["data"]["TotalEquipsScore"])
    basic_info.append(data["data"]["MatchDetail"]["totalLift"])
    kungfuInstance = Kungfu.with_internel_id(data["data"]["Kungfu"]["KungfuID"])
    kungfu = kungfuInstance.name
    if kungfu == "山居剑意":
        kungfu = "问水诀"
    type = kungfuInstance.base
    if type in ["根骨", "元气", "身法", "力道"]:
        basic_info_key.append(type)
        basic_info_key = basic_info_key + ["面板攻击", "基础攻击", "会心", "会心效果", "加速", "破防", "无双", "破招", "御劲", "化劲"]
        type_to_attr = {
            "根骨": "atSpiritBase",
            "元气": "atSpunkBase",
            "身法": "atAgilityBase",
            "力道": "atStrengthBase"
        }
        basic_info = basic_info + [
            str(data["data"]["MatchDetail"][type_to_attr[type]]), 
            str(data["data"]["MatchDetail"]["totalAttack"]), 
            str(data["data"]["MatchDetail"]["baseAttack"]), 
            str(data["data"]["MatchDetail"]["atCriticalStrikeLevel"]), 
            str(data["data"]["MatchDetail"]["atCriticalDamagePowerBaseLevel"]) + "%", 
            str(data["data"]["MatchDetail"]["atHasteBaseLevel"]), 
            str(data["data"]["MatchDetail"]["atOvercomeBaseLevel"]) + "%", 
            str(data["data"]["MatchDetail"]["atStrainBaseLevel"]) + "%", 
            str(data["data"]["MatchDetail"]["atSurplusValueBase"]), 
            str(data["data"]["MatchDetail"]["atToughnessBaseLevel"]) + "%", 
            str(data["data"]["MatchDetail"]["atDecriticalDamagePowerBaseLevel"]) + "%" 
            ]
    elif type == "治疗":
        basic_info_key.append("根骨")
        basic_info_key = basic_info_key + ["治疗量", "会心", "会心效果", "加速", "御劲", "化劲"]
        basic_info = basic_info + [
            str(data["data"]["MatchDetail"]["atSpiritBase"]),
            str(data["data"]["MatchDetail"]["totaltherapyPowerBase"]),
            str(data["data"]["MatchDetail"]["atCriticalStrikeLevel"]), 
            str(data["data"]["MatchDetail"]["atCriticalDamagePowerBaseLevel"]) + "%", 
            str(data["data"]["MatchDetail"]["atHasteBaseLevel"]), 
            str(data["data"]["MatchDetail"]["atToughnessBaseLevel"]) + "%", 
            str(data["data"]["MatchDetail"]["atDecriticalDamagePowerBaseLevel"]) + "%" 
        ]
    elif type == "防御":
        basic_info_key.append("体质")
        basic_info_key = basic_info_key + ["外防", "内防", "御劲", "闪避", "招架", "拆招", "加速", "无双", "破招", "化劲"]
        basic_info = basic_info + [
            str(data["data"]["MatchDetail"]["atVitalityBase"]),
            str(data["data"]["MatchDetail"]["atPhysicsShieldBaseLevel"]) + "%",
            str(data["data"]["MatchDetail"]["atMagicShieldLevel"]) + "%",
            str(data["data"]["MatchDetail"]["atToughnessBaseLevel"]) + "%",
            str(data["data"]["MatchDetail"]["atDodgeLevel"]) + "%",
            str(data["data"]["MatchDetail"]["atParryBaseLevel"]) + "%",
            str(data["data"]["MatchDetail"]["atParryValue"]),
            str(data["data"]["MatchDetail"]["atHasteBaseLevel"]),
            str(data["data"]["MatchDetail"]["atStrainBaseLevel"]) + "%",
            str(data["data"]["MatchDetail"]["atSurplusValueBase"]),
            str(data["data"]["MatchDetail"]["atDecriticalDamagePowerBaseLevel"]) + "%"
        ]
    qixue = ["未知"] * 12
    qixue_image = [build_path(ASSETS, ["image", "jx3", "attributes", "unknown.png"])] * 12
    for qixue_ in data["data"]["Person"]["qixueList"]:
        qixueInstance = await Qixue.create(qixue_, kungfu=kungfuInstance.name or "")
        location = qixueInstance.location
        if location is None:
            continue
        x, y, icon = location
        qixue[int(x)-1] = qixue_["name"]
        qixue_image[int(x)-1] = icon

    table = []

    school = kungfuInstance.school
    if not school:
        school = ""

    html = str(
        SimpleHTML(
            "jx3",
            "attribute_v4",
            panel_key = json.dumps(basic_info_key, ensure_ascii=False),
            panel_value = json.dumps(basic_info, ensure_ascii=False),
            qixue_name = json.dumps(qixue, ensure_ascii=False),
            qixue_img = json.dumps(qixue_image, ensure_ascii=False),
            background = build_path(ASSETS, ["image", "jx3", "assistance", "10.jpg"]),
            table_content = "{{ table_content }}",
            font = build_path(ASSETS, ["font", "custom.ttf"]),
            school = build_path(ASSETS, ["image", "school", school + ".svg"]),
            color = kungfuInstance.color
        )
    )
    for location in ["帽子", "上衣", "腰带", "护臂", "裤子", "鞋", "项链", "腰坠", "戒指", "戒指", "投掷囊"]: # 武器单独适配，此处适配全身除武器以外的
        for each_location in data["data"]["Equips"]:
            if each_location["Icon"]["SubKind"] == location:
                eicon = each_location["Icon"]["FileName"]
                ename = each_location["Name"] + "（" + each_location["Quality"] + "）"
                eattr = get_equip_attr(each_location["ModifyType"], type) # type: ignore
                ecurrent_strength = each_location["StrengthLevel"]
                emax_strength = each_location["MaxStrengthLevel"]
                erest_strength = str(int(emax_strength) - int(ecurrent_strength))
                ecurrent_strength = int(ecurrent_strength) * "★"
                erest_strength = int(erest_strength) * "★"
                if location == "戒指":
                    fivestones = "不适用"
                else:
                    fivestones = []
                    for each_hole in each_location["FiveStone"]:
                        fivestones.append("<img width=\"32px\" height=\"32px\" src=\"" + build_path(ASSETS, ["image", "jx3", "attributes", "wuxingshi", str(each_hole["Level"]) + ".png"]) + "\" style=\"vertical-align: middle;\">")
                    fivestones = "\n".join(fivestones)
                common_enchant_flag = False
                permanent_enchant_flag = False
                if "WCommonEnchant" in each_location:
                    common_enchant_flag = True
                    attrs_ = json.dumps(each_location["ModifyType"], ensure_ascii=False)
                    if attrs_.find("攻击") != -1:
                        type_ = "伤"
                    elif attrs_.find("治疗") != -1:
                        type_ = "疗"
                    else:
                        type_ = "御"
                    common_enchant_name = str(Enchant(each_location["Quality"]).name) + "·" + type_ + "·" + location_mapping(location)
                if "WPermanentEnchant" in each_location:
                    permanent_enchant_flag = True
                    permanent_enchant_name = each_location["WPermanentEnchant"]["Name"]
                if permanent_enchant_flag and common_enchant_flag:
                    display_enchant = "<img src=\"" + build_path(ASSETS, ["image", "jx3", "attributes", "common_enchant.png"]) + "\" style=\"vertical-align: middle;\"><img src=\"" + build_path(ASSETS, ["image", "jx3", "attributes", "permanent_enchant.png"]) + "\" style=\"vertical-align: middle;\">" + permanent_enchant_name
                else:
                    if permanent_enchant_flag and not common_enchant_flag:
                        display_enchant = "<img src=\"" + build_path(ASSETS, ["image", "jx3", "attributes", "permanent_enchant.png"]) + "\" style=\"vertical-align: middle;\">" + permanent_enchant_name
                    elif common_enchant_flag and not permanent_enchant_flag:
                        display_enchant = "<img src=\"" + build_path(ASSETS, ["image", "jx3", "attributes", "common_enchant.png"]) + "\" style=\"vertical-align: middle;\">" + common_enchant_name
                    else:
                        display_enchant = ""
                source = each_location["equipBelongs"]
                if source == []:
                    source = ""
                else:
                    try:
                        source = source[0]["source"].split("；")[0].replace(" — ", "<br>")
                    except:
                        source = ""
                data["data"]["Equips"].remove(each_location)
                table.append(
                    Template(template_attrs_v4).render(
                        icon = eicon,
                        name = ename,
                        attr = eattr,
                        enable = ecurrent_strength,
                        available = erest_strength,
                        fivestone = fivestones,
                        enchant = display_enchant,
                        source = source
                    )
                )
            else:
                continue
    for each_location in data["data"]["Equips"]:
        eicon = each_location["Icon"]["FileName"]
        ename = each_location["Name"] + "（" + each_location["Quality"] + "）"
        eattr = get_equip_attr(each_location["ModifyType"], type) # type: ignore
        ecurrent_strength = each_location["StrengthLevel"]
        emax_strength = each_location["MaxStrengthLevel"]
        erest_strength = str(int(emax_strength) - int(ecurrent_strength))
        ecurrent_strength = int(ecurrent_strength) * "★"
        erest_strength = int(erest_strength) * "★"
        fivestones = []
        fivestones_flag = True
        try:
            five_stones_data = each_location["FiveStone"]
        except:
            fivestones_flag = False
        if fivestones_flag:
            for each_hole in five_stones_data:
                fivestones.append("<img src=\"" + build_path(ASSETS, ["image", "jx3", "attributes", "wuxingshi", str(each_hole["Level"]) + ".png"]) + "\" style=\"vertical-align: middle;\" width=\"32px\" height=\"32px\">")
            fivestones = "\n".join(fivestones)
        else:
            fivestones = ""
        permanent_enchant_flag = False
        colorful_stone_flag = False
        if "WPermanentEnchant" in each_location:
            permanent_enchant_flag = True
            permanent_enchant_name = each_location["WPermanentEnchant"]["Name"]
        if "effectColorStone" in each_location:
            colorful_stone_flag = True
            colorful_stone_name = each_location["effectColorStone"]["Name"]
            colorful_stone_image = each_location["effectColorStone"]["Icon"]["FileName"]
        if permanent_enchant_flag and colorful_stone_flag:
            display_enchant = "<img src=\"" + build_path(ASSETS, ["jx3", "attributes", "permanent_enchant.png"]) + "\" style=\"vertical-align: middle;\"><img width=\"32px\" height=\"32px\" src=\"" + colorful_stone_image + "\" style=\"vertical-align: middle;\">" + colorful_stone_name
        else:
            if permanent_enchant_flag and not colorful_stone_flag:
                display_enchant = "<img src=\"" + build_path(ASSETS, ["jx3", "attributes", "permanent_enchant.png"]) + "\" style=\"vertical-align: middle;\">" + permanent_enchant_name
            elif colorful_stone_flag and not permanent_enchant_flag:
                display_enchant = "<img width=\"32px\" height=\"32px\" src=\"" + colorful_stone_image + "\" style=\"vertical-align: middle;\">" + colorful_stone_name
            else:
                display_enchant = ""
        source = each_location["equipBelongs"]
        if source == []:
            source = ""
        else:
            try:
                source = source[0]["source"].split("；")[0].replace(" — ", "<br>")
            except:
                source = ""
        table.append(
            Template(template_attrs_v4).render(
                icon = eicon,
                name = ename,
                attr = eattr,
                enable = ecurrent_strength,
                available = erest_strength,
                fivestone = fivestones,
                enchant = display_enchant,
                source = source
            )
        )
    html = Template(html).render(
        table_content = "\n".join(table)
    )
    final_path = await generate(html, "", False, viewport={"width": 2200, "height": 1250}, full_screen=True) 
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()