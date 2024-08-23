from pathlib import Path
from typing import Optional

from src.constant.jx3 import kungfu_to_school

from src.tools.utils.request import get_api
from src.tools.config import Config
from src.tools.utils.file import read, write
from src.tools.basic.server import server_mapping, Zone_mapping
from src.tools.basic.prompts import PROMPT
from src.tools.basic.jx3 import gen_ts, format_body, gen_xsk
from src.tools.utils.request import post_url
from src.tools.generate import get_uuid, generate
from src.tools.utils.path import ASSETS, CACHE, PLUGINS, VIEWS

from src.plugins.jx3.bind import get_player_local_data
from src.plugins.jx3.affection import getColor

from .api import kungfu_mapping, enchant_mapping, find_qx

import json

token = Config.jx3.api.token
ticket= Config.jx3.api.ticket
device_id = ticket.split("::")[-1]

template_attrs_v4 = """
<tr>
    <td><img width=\"80px\" height=\"80px\" src="$icon"></td>
    <td>$name<br>$attr</td>
    <td><span style="color:gold">$enable</span><span style="color:grey"></span>$available<br>$fivestone</td>
    <td>
        $enchant
    </td>
    <td>$source</td>
</tr>"""

async def get_basic_info(server: str, name: str):
    data = await get_player_local_data(role_name=name, server_name=server)
    data = data.format_jx3api()
    if data["code"] != 200:
        return 404
    else:
        data = data["data"]
        tuilan_status = "已绑定" if data.get("personId") != "" else "未绑定"
        return [data.get("roleName"), str(data.get("roleId")), data.get("tongName"), data.get("forceName"), data.get("bodyName"), data.get("campName"), tuilan_status]

def school_mapping(school_num: int) -> Optional[str]:
    map = json.loads(read(PLUGINS + "/jx3/attributes/schoolmapping.json"))
    for i in map:
        if map[i] == school_num:
            return i
        
def get_qixue_place(qixueList: dict, qixueName: str) -> Optional[int]:
    for a in qixueList:
        for b in qixueList[a]:
            if qixueList[a][b]["name"] == qixueName:
                return int(a)
            
def insert_multiple_elements(single_list, elements_positions):
    elements_positions.sort(key=lambda x: x[1], reverse=True)
    for element, position in elements_positions:
        single_list.insert(position, element)
    return single_list

def location_mapping(location: str):
    return {
        "帽子": "帽",
        "上衣": "衣",
        "腰带": "腰",
        "护臂": "腕",
        "鞋": "鞋"
    }[location]

def get_equip_attr(data: list, job: str):
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
            attr = attr.replace(y, "")
        if attr != "":
            if job == "防御":
                msg = msg + f" {attr[0]}"
            else:
                msg = msg + f" {attr}"
    return msg

async def get_attrs_v4(server: Optional[str], name: str, group_id: str):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    basic_info = await get_basic_info(server, name)
    if basic_info == 404:
        return [f"唔……未找到该玩家，请提交角色！\n提交角色 服务器 UID"]
    param = {
        "zone": Zone_mapping(server),
        "server": server,
        "game_role_id": basic_info[1],
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host": "m.pvp.xoyo.com",
        "Accept": "application/json",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "cache-control": "no-cache",
        "fromsys": "APP",
        "clientkey": "1",
        "apiversion": "3",
        "gamename": "jx3",
        "platform": "ios",
        "sign": "true",
        "token": ticket,
        "deviceid": device_id,
        "User-Agent": "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
        "x-sk": xsk
    }
    data = await post_url(url="https://m.pvp.xoyo.com/mine/equip/get-role-equip", data=param, headers=headers)
    data = json.loads(data)
    basic_info_key = ["角色名", "UID", "帮会", "门派", "体型", "阵营", "推栏", "装分", "气血"]
    basic_info.append(data["data"]["TotalEquipsScore"])
    basic_info.append(data["data"]["MatchDetail"]["totalLift"])
    kungfu = school_mapping(data["data"]["Kungfu"]["KungfuID"])
    if kungfu == "山居剑意":
        kungfu = "问水诀"
    type = kungfu_mapping(kungfu)
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
    qixue = ["未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知"]
    qixueImg = [
        PLUGINS + "/jx3/attributes/unknown.png",
        PLUGINS + "/jx3/attributes/unknown.png",
        PLUGINS + "/jx3/attributes/unknown.png",
        PLUGINS + "/jx3/attributes/unknown.png",
        PLUGINS + "/jx3/attributes/unknown.png",
        PLUGINS + "/jx3/attributes/unknown.png",
        PLUGINS + "/jx3/attributes/unknown.png",
        PLUGINS + "/jx3/attributes/unknown.png",
        PLUGINS + "/jx3/attributes/unknown.png", 
        PLUGINS + "/jx3/attributes/unknown.png",
        PLUGINS + "/jx3/attributes/unknown.png",
        PLUGINS + "/jx3/attributes/unknown.png"
    ]
    if data["data"]["Person"]["qixueList"] != []:
        versions = await get_api("https://data.jx3box.com/talent/index.json")
        for i in versions:
            if i["name"].find("体服") != -1:
                continue
            else:
                ver = i["version"]
                break
        qxdata = await get_api(f"https://data.jx3box.com/talent/{ver}.json")
        for i in data["data"]["Person"]["qixueList"]:
            qxname = i["name"]
            place = find_qx(qxdata, kungfu, qxname)
            if place == None:
                continue
            else:
                qixue[place] = qxname
                qixueImg[place] = i["icon"]["FileName"]
    else:
        pass
    table = []
    html = read(VIEWS + "/jx3/equip/attributes_v4.html")
    html = html.replace("$panel_key", json.dumps(basic_info_key, ensure_ascii=False))
    html = html.replace("$panel_value", json.dumps(basic_info, ensure_ascii=False))
    html = html.replace("$qixue_name", json.dumps(qixue, ensure_ascii=False))
    html = html.replace("$qixue_img", json.dumps(qixueImg, ensure_ascii=False))
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
                        fivestones.append("<img width=\"32px\" height=\"32px\" src=\"" + ASSETS + "/wuxingshi/" + each_hole["Level"] + ".png" + "\" style=\"vertical-align: middle;\">")
                    fivestones = "\n".join(fivestones)
                henchant_flag = False
                lenchant_flag = False
                if "WCommonEnchant" in each_location:
                    henchant_flag = True
                    attrs_ = json.dumps(each_location["ModifyType"], ensure_ascii=False)
                    if attrs_.find("攻击") != -1:
                        type_ = "伤"
                    elif attrs_.find("治疗") != -1:
                        type_ = "疗"
                    else:
                        type_ = "御"
                    henchant_name = enchant_mapping(each_location["Quality"]) + "·" + type_ + "·" + location_mapping(location) # type: ignore
                if "WPermanentEnchant" in each_location:
                    lenchant_flag = True
                    lenchant_name = each_location["WPermanentEnchant"]["Name"]
                if lenchant_flag and henchant_flag:
                    display_enchant = "<img src=\"" + PLUGINS + "/jx3/attributes/henchant.png" + "\" style=\"vertical-align: middle;\"><img src=\"" + PLUGINS + "/jx3/attributes/lenchant.png" + "\" style=\"vertical-align: middle;\">" + lenchant_name
                else:
                    if lenchant_flag and not henchant_flag:
                        display_enchant = "<img src=\"" + PLUGINS + "/jx3/attributes/lenchant.png" + "\" style=\"vertical-align: middle;\">" + lenchant_name
                    elif henchant_flag and not lenchant_flag:
                        display_enchant = "<img src=\"" + PLUGINS + "/jx3/attributes/henchant.png" + "\" style=\"vertical-align: middle;\">" + henchant_name
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
                table.append(template_attrs_v4.replace("$icon", eicon).replace("$name", ename).replace("$attr", eattr).replace("$enable", ecurrent_strength).replace("$available", erest_strength).replace("$fivestone", fivestones).replace("$enchant", display_enchant).replace("$source", source))
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
                fivestones.append("<img src=\"" + ASSETS + "/wuxingshi/" + each_hole["Level"] + ".png" + "\" style=\"vertical-align: middle;\" width=\"32px\" height=\"32px\">")
            fivestones = "\n".join(fivestones)
        else:
            fivestones = ""
        lenchant_flag = False
        colorful_stone_flag = False
        if "WPermanentEnchant" in each_location:
            lenchant_flag = True
            lenchant_name = each_location["WPermanentEnchant"]["Name"]
        if "effectColorStone" in each_location:
            colorful_stone_flag = True
            colorful_stone_name = each_location["effectColorStone"]["Name"]
            colorful_stone_image = each_location["effectColorStone"]["Icon"]["FileName"]
        if lenchant_flag and colorful_stone_flag:
            display_enchant = "<img src=\"" + PLUGINS + "/jx3/attributes/lenchant.png" + "\" style=\"vertical-align: middle;\"><img width=\"32px\" height=\"32px\" src=\"" + colorful_stone_image + "\" style=\"vertical-align: middle;\">" + colorful_stone_name
        else:
            if lenchant_flag and not colorful_stone_flag:
                display_enchant = "<img src=\"" + PLUGINS + "/jx3/attributes/lenchant.png" + "\" style=\"vertical-align: middle;\">" + lenchant_name
            elif colorful_stone_flag and not lenchant_flag:
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
        table.append(template_attrs_v4.replace("$icon", eicon).replace("$name", ename).replace("$attr", eattr).replace("$enable", ecurrent_strength).replace("$available", erest_strength).replace("$fivestone", fivestones).replace("$enchant", display_enchant).replace("$source", source))
    final_table = "\n".join(table)
    font = ASSETS + "/font/custom.ttf"
    school = kungfu_to_school(kungfu) # type: ignore
    if not school:
        school = ""
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$school", ASSETS + "/image/school/" + school + ".svg").replace("$color", getColor(school))
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "", False, viewport={"width": 2200, "height": 1250}, full_screen=True) 
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()
