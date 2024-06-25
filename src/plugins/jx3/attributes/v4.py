from src.tools.basic import *
from src.plugins.jx3.rank.school_rank import colors

from .api import kungfu_mapping, enchant_mapping

template_attrs_v4 = """
<tr>
    <td><img src="$icon"></td>
    <td>$name<br>$attr</td>
    <td><span style="color:gold">$enable</span><span style="color:grey"></span>$available</td>
    <td>
        $fivestone
    <td>
        $enchant
    </td>
    <td>$source</td>
</tr>"""

async def get_basic_info(server: str, name: str):
    data = await get_api(f"https://www.jx3api.com/data/role/detailed?token={token}&server={server}&name={name}")
    if data["code"] != 200:
        return 404
    else:
        data = data["data"]
        tuilan_status = "已绑定" if data.get("personId") != "" else "未绑定"
        return [data.get("roleName"), str(data.get("roleId")), data.get("tongName"), data.get("forceName"), data.get("bodyName"), data.get("campName"), tuilan_status]

def school_mapping(school_num: int) -> str:
    map = json.loads(read(PLUGINS + "/jx3/attributes/schoolmapping.json"))
    for i in map:
        if map[i] == school_num:
            return i
        
def get_qixue_place(qixueList: dict, qixueName: str) -> int:
    for a in qixueList:
        for b in a:
            if qixueList[a][b] == qixueName:
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

async def get_attrs_v4(server: str, name: str, group_id: str):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    basic_info = await get_basic_info(server, name)
    if basic_info == 404:
        return ["唔……未找到该玩家，请检查角色名称或服务器后重试！"]
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
        "token": token,
        "deviceid": device_id,
        "User-Agent": "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
        "x-sk": xsk
    }
    data = await post_url(url="https://m.pvp.xoyo.com/mine/equip/get-role-equip", data=param, headers=headers)
    basic_info_key = ["角色名", "UID", "帮会", "门派", "体型", "阵营", "推栏", "装分", "气血"]
    basic_info.append(data["data"]["TotalEquipsScore"])
    basic_info.append(data["data"]["totalLift"])
    kungfu = school_mapping(data["data"]["Kungfu"]["KungfuID"])
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
            str(data["data"]["MuchDetail"][type_to_attr[type]]), 
            str(data["data"]["MuchDetail"]["totalAttack"]), 
            str(data["data"]["MuchDetail"]["baseAttack"]), 
            str(data["data"]["MuchDetail"]["atCriticalStrikeLevel"]), 
            str(data["data"]["MuchDetail"]["atCriticalDamagePowerBaseLevel"]) + "%", 
            str(data["data"]["MuchDetail"]["atHasteBaseLevel"]), 
            str(data["data"]["MuchDetail"]["atOvercomeBaseLevel"]) + "%", 
            str(data["data"]["MuchDetail"]["atStrainBaseLevel"]) + "%", 
            str(data["data"]["MuchDetail"]["atSurplusValueBase"]), 
            str(data["data"]["MuchDetail"]["atToughnessBaseLevel"]) + "%", 
            str(data["data"]["MuchDetail"]["atDecriticalDamagePowerBaseLevel"]) + "%" 
            ]
    elif type == "治疗":
        basic_info_key.append("根骨")
        basic_info_key = basic_info_key + ["治疗量", "会心", "会心效果", "加速", "御劲", "化劲"]
        basic_info = basic_info + [
            str(data["data"]["MuchDetail"]["atSpiritBase"]),
            str(data["data"]["MuchDetail"]["totaltherapyPowerBase"]),
            str(data["data"]["MuchDetail"]["atCriticalStrikeLevel"]), 
            str(data["data"]["MuchDetail"]["atCriticalDamagePowerBaseLevel"]) + "%", 
            str(data["data"]["MuchDetail"]["atHasteBaseLevel"]), 
            str(data["data"]["MuchDetail"]["atToughnessBaseLevel"]) + "%", 
            str(data["data"]["MuchDetail"]["atDecriticalDamagePowerBaseLevel"]) + "%" 
        ]
    elif type == "防御":
        basic_info_key.append("体质")
        basic_info_key = basic_info_key + ["外防", "内防", "御劲", "闪避", "招架", "拆招", "加速", "无双", "破招", "化劲"]
        basic_info = basic_info + [
            str(data["data"]["MuchDetail"]["atVitalityBase"]),
            str(data["data"]["MuchDetail"]["atPhysicsShieldBaseLevel"]) + "%",
            str(data["data"]["MuchDetail"]["atMagicShieldLevel"]) + "%",
            str(data["data"]["MuchDetail"]["atToughnessBaseLevel"]) + "%",
            str(data["data"]["MuchDetail"]["atDodgeLevel"]) + "%",
            str(data["data"]["MuchDetail"]["atParryBaseLevel"]) + "%",
            str(data["data"]["MuchDetail"]["atParryValue"]),
            str(data["data"]["MuchDetail"]["atHasteBaseLevel"]),
            str(data["data"]["MuchDetail"]["atStrainBaseLevel"]) + "%",
            str(data["data"]["MuchDetail"]["atSurplusValueBase"]),
            str(data["data"]["MuchDetail"]["atDecriticalDamagePowerBaseLevel"]) + "%"
        ]
    if data["data"]["Person"]["qixueList"] == []:
        qixue_Confirmed = []
        qixueCImg = []
        qixue_Looking = []
        qixueLImg = []
        for i in data["data"]["Person"]["qixueList"]:
            if i["level"] == 0:
                qixue_Looking.append(i["name"])
                qixueCImg.append(i["icon"]["FileName"])
            else:
                qixue_Confirmed.append(i["name"])
                qixueLImg.append(i["icon"]["FileName"])
        name_positions = []
        img_positions = []
        versions = await get_api("https://data.jx3box.com/talent/index.json")
        for i in versions:
            if i["name"].find("体服") != -1:
                continue
            else:
                ver = i["version"]
                break
        qxdata = await get_api(f"https://data.jx3box.com/talent/{ver}.json")
        for i in range(len(qixue_Looking)):
            place = qxdata, qixue_Looking[i]
            name_positions.apppend((qixue_Looking[i], place))
            img_positions.append((qixueLImg[i], place))
        qixue = insert_multiple_elements(qixue_Confirmed, name_positions) # 奇穴列表
        qixueImg = insert_multiple_elements(qixueLImg, img_positions) # 奇穴图片列表
    else:
        qixue = []
        for i in range(12):
            qixue.append("未知")
            qixueImg.append(PLUGINS + "/jx3/attributes/unknown.png")
    table = []
    html = read(VIEWS + "/jx3/equip/attributes.html")
    html = html.replace("$panel_key", json.dumps(basic_info_key, ensure_ascii=False))
    html = html.replace("$panel_value", json.dumps(basic_info, ensure_ascii=False))
    html = html.replace("$qixue_name", json.dumps(qixue, ensure_ascii=False))
    html = html.replace("$qixue_img", json.dumps(qixueImg, ensure_ascii=False))
    for location in ["帽子", "上衣", "腰带", "护臂", "裤子", "鞋", "项链", "腰坠", "戒指", "投掷囊"]: # 武器单独适配，此处适配全身除武器以外的
        for each_location in data["data"]["Equips"]:
            if each_location["Icon"]["SubKind"] == location:
                eicon = each_location["Icon"]["FileName"]
                ename = each_location["Name"] + "（" + each_location["Quality"] + "）"
                eattr = get_equip_attr(each_location["ModifyType"])
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
                        fivestones.append("<img src=\"" + ASSETS + "/wuxingshi/" + each_hole["Level"] + ".png" + "\" style=\"vertical-align: middle;\" width=\"20px\" height=\"20px\">")
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
                    henchant_name = enchant_mapping(each_location["Quality"]) + "·" + type_ + location_mapping(location)
                if "WPermanentEnchant" in each_location:
                    lenchant_flag = True
                    lenchant_name = each_location["WPermanentEnchant"]["Name"]
                if lenchant_flag and henchant_flag:
                    display_enchant = "<img src=\"" + PLUGINS + "/jx3/attributes/henchant.png" + "\" style=\"vertical-align: middle;\"><img src=\"" + PLUGINS + "/jx3/attributes/lenchant.png" + "\" style=\"vertical-align: middle;\">" + lenchant_name
                else:
                    if lenchant_flag and not henchant_flag:
                        display_enchant = "<img src=\"" + PLUGINS + "/jx3/attributes/lenchant.png" + "\" style=\"vertical-align: middle;\">" + lenchant_name
                    elif henchant_flag and not lenchant_name:
                        display_enchant = "<img src=\"" + PLUGINS + "/jx3/attributes/henchant.png" + "\" style=\"vertical-align: middle;\">" + henchant_name
                    else:
                        display_enchant = ""
                source = each_location["equipBelongs"]
                if source == []:
                    source = ""
                else:
                    source = source[0]["source"].split("；")[0]
                data["data"]["Equips"].remove(each_location)
                table.append(template_attrs_v4.replace("$icon", eicon).replace("$name", ename).replace("$attr", eattr).replace("$enable", ecurrent_strength).replace("$available", erest_strength).replace("$fivestone", fivestones).replace("$enchant", display_enchant).replace("$source", source))
            else:
                continue
    for each_location in data["data"]["Equips"]:
        eicon = each_location["Icon"]["FileName"]
        ename = each_location["Name"] + "（" + each_location["Quality"] + "）"
        eattr = get_equip_attr(each_location["ModifyType"])
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
                fivestones.append("<img src=\"" + ASSETS + "/wuxingshi/" + each_hole["Level"] + ".png" + "\" style=\"vertical-align: middle;\" width=\"20px\" height=\"20px\">")
            fivestones = "\n".join(fivestones)
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
            display_enchant = "<img src=\"" + PLUGINS + "/jx3/attributes/henchant.png" + "\" style=\"vertical-align: middle;\"><img src=\"" + PLUGINS + "/jx3/attributes/lenchant.png" + "\" style=\"vertical-align: middle;\">" + lenchant_name
        else:
            if lenchant_flag and not colorful_stone_flag:
                display_enchant = "<img src=\"" + colorful_stone_image + "\" style=\"vertical-align: middle;\">" + lenchant_name
            elif colorful_stone_flag and not lenchant_name:
                display_enchant = "<img src=\"" + colorful_stone_image + "\" style=\"vertical-align: middle;\">" + colorful_stone_name
            else:
                display_enchant = ""
        source = each_location["equipBelongs"]
        if source == []:
            source = ""
        else:
            source = source[0]["source"].split("；")[0]
        data["data"]["Equips"].remove(each_location)
        table.append(template_attrs_v4.replace("$icon", eicon).replace("$name", ename).replace("$attr", eattr).replace("$enable", ecurrent_strength).replace("$available", erest_strength).replace("$fivestone", fivestones).replace("$enchant", display_enchant).replace("$source", source))
    final_table = "\n".join(table)
    font = ASSETS + "/font/custom.ttf"
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$school", basic_info[3]).replace("$color", colors[basic_info[3]])
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()
