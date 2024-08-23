from PIL import Image, ImageFont, ImageDraw

from src.constant.jx3 import kungfu_to_school

from src.tools.generate import get_uuid
from src.tools.basic.jx3 import gen_ts, gen_xsk, format_body
from src.tools.utils.path import ASSETS, CACHE, PLUGINS
from src.tools.config import Config
from src.tools.utils.request import post_url

ticket = Config.jx3.api.ticket
device_id = ticket.split("::")[-1]

from ..attributes.api import (
    kungfu_mapping,
    get_fs,
    local_save, 
    get_kf_icon,
    get_bg,
    data_process,
    enchant_mapping,
    judge_special_weapon
)

import json

async def get_recommended_equips_list(forceId: str, condition):
    param = {
        "Kungfu": forceId,
        "EquipTags": condition,
        "Size": 10,
        "cursor": 0,
        "matchSeasonId": "6629cd12ba3129001275fc58", # 赛季标识
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host": "m.pvp.xoyo.com",
        "accept": "application/json",
        "deviceid": device_id,
        "platform": "android",
        "gamename": "jx3",
        "clientkey": "1",
        "fromsys": "APP",
        "cache-control": "no-cache",
        "apiversion": "3",
        "sign": "true",
        "token": ticket,
        "content-Type": "application/json",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/3.12.2",
        "x-sk": xsk
    }
    info = await post_url(url="https://m.pvp.xoyo.com/socialgw/dynamic/equip/query", data=param, headers=headers)
    info = json.loads(info)
    data = []
    name = []
    tag = []
    like = []
    author = []
    for i in info["data"]["data"]:
        data.append(json.loads(i["matchEquip"]["equips"]))
        name.append(i["matchEquip"]["name"])
        tag.append(i["matchEquip"]["tags"][0])
        author.append(i["nickname"])
        like.append(str(i["likeCount"]))
    return [data, name, tag, author, like]  # 数据，配装名称，标签，作者


def att_mapping(att):
    if att == "根骨":
        return "atSpiritBase"
    elif att == "力道":
        return "atStrengthBase"
    elif att == "元气":
        return "atSpunkBase"
    elif att == "身法":
        return "atAgilityBase"


async def get_single_recequips(data: dict, author: str, name: str, tag: str, kf: str):
    score = str(data["matchDetail"]["score"])
    basic = [score, name, author, tag]
    if kf == "山居剑意":
        kf = "问水诀"
    att = kungfu_mapping(kf)
    if att in ["根骨", "元气", "力道", "身法"]:
        flag = 1
    elif att == "治疗":
        flag = 2
    elif att == "防御":
        flag = 3
    equip_data = data_process(kf, data, False)
    maxjl_list = []
    jl_list = []
    equip_list = []
    equip_icon_list = []
    equip_quailty = []
    henchant = ["", "", "", "", "", ""]
    lenchant = ["", "", "", "", "", "", "", "", "", "", "", ""]
    if kf in ["问水诀", "山居剑意"]:
        lenchant.append("")
    for i in equip_data:
        if i == "":
            equip_quailty.append("")
        else:
            msg = i["Quality"] # type: ignore
            for x in i["ModifyType"]: # type: ignore
                content = x["Attrib"]["GeneratedMagic"].split("提高") # type: ignore
                if len(content) == 1:
                    content = content[0].split("增加")
                attr = content[0]
                attr = attr.replace("外功防御", "外防")
                attr = attr.replace("内功防御", "内防")
                attr = attr.replace("会心效果", "会效")
                filter_string = ["全", "阴性", "阳性", "阴阳", "毒性", "攻击", "值", "成效", "内功", "外功", "体质",
                                 "根骨", "力道", "元气", "身法", "等级", "混元性", "招式产生威胁", "水下呼吸时间", "抗摔系数", "马术气力上限"]
                for y in filter_string:
                    attr = attr.replace(y, "")
                if attr != "":
                    msg = msg + f" {attr}"
            equip_quailty.append(msg)
    for i in equip_data:
        if i == "":
            maxjl_list.append(6)
            jl_list.append(0)
            equip_list.append("")
            equip_icon_list.append("")
        else:
            maxjl_list.append(i["MaxStrengthLevel"]) # type: ignore
            jl_list.append(i["StrengthLevel"]) # type: ignore
            equip_list.append(i["Name"] + "(" + i["StrengthLevel"] + # type: ignore
                              "/" + i["MaxStrengthLevel"] + ")") # type: ignore
            equip_icon_list.append(i["Icon"]["FileName"]) # type: ignore
    for i in equip_data:
        if i["Icon"]["SubKind"] == "帽子": # type: ignore
            if "WCommonEnchant" in list(i):
                attrs_ = json.dumps(i["ModifyType"], ensure_ascii=False) # type: ignore
                if attrs_.find("攻击") != -1:
                    type_ = "伤"
                elif attrs_.find("治疗") != -1:
                    type_ = "疗"
                else:
                    type_ = "御"
                name = enchant_mapping(i["Quality"]) + "·" + type_ + "·帽" # type: ignore
                henchant[0] = name
            else:
                henchant[0] = ""
        elif i["Icon"]["SubKind"] == "上衣": # type: ignore
            if "WCommonEnchant" in list(i):
                attrs_ = json.dumps(i["ModifyType"], ensure_ascii=False) # type: ignore
                if attrs_.find("攻击") != -1:
                    type_ = "伤"
                elif attrs_.find("治疗") != -1:
                    type_ = "疗"
                else:
                    type_ = "御"
                name = enchant_mapping(i["Quality"]) + "·" + type_ + "·衣" # type: ignore
                henchant[1] = name
            else:
                henchant[1] = ""
        elif i["Icon"]["SubKind"] == "腰带": # type: ignore
            if "WCommonEnchant" in list(i):
                attrs_ = json.dumps(i["ModifyType"], ensure_ascii=False) # type: ignore
                if attrs_.find("攻击") != -1:
                    type_ = "伤"
                elif attrs_.find("治疗") != -1:
                    type_ = "疗"
                else:
                    type_ = "御"
                name = enchant_mapping(i["Quality"]) + "·" + type_ + "·腰" # type: ignore
                henchant[2] = name
            else:
                henchant[2] = ""
        elif i["Icon"]["SubKind"] == "护臂": # type: ignore
            if "WCommonEnchant" in list(i):
                attrs_ = json.dumps(i["ModifyType"], ensure_ascii=False) # type: ignore
                if attrs_.find("攻击") != -1:
                    type_ = "伤"
                elif attrs_.find("治疗") != -1:
                    type_ = "疗"
                else:
                    type_ = "御"
                name = enchant_mapping(i["Quality"]) + "·" + type_ + "·腕" # type: ignore
                henchant[3] = name
            else:
                henchant[3] = ""
        elif i["Icon"]["SubKind"] == "鞋": # type: ignore
            if "WCommonEnchant" in list(i):
                attrs_ = json.dumps(i["ModifyType"], ensure_ascii=False) # type: ignore
                if attrs_.find("攻击") != -1:
                    type_ = "伤"
                elif attrs_.find("治疗") != -1:
                    type_ = "疗"
                else:
                    type_ = "御"
                name = enchant_mapping(i["Quality"]) + "·" + type_ + "·鞋" # type: ignore
                henchant[4] = name
            else:
                henchant[4] = ""
    num = 0
    for i in equip_data:
        if i != "":
            if "WPermanentEnchant" in list(i):
                lenchant[num] = i["WPermanentEnchant"]["Name"] # type: ignore
                num = num + 1
            else:
                num = num + 1
                continue
        else:
            num = num + 1
            continue
    fs = []
    for i in equip_data:
        try:
            i["FiveStone"] # type: ignore
        except Exception as _:
            continue
        for x in i["FiveStone"]: # type: ignore
            if x["Name"] != "" or int(x["Level"]) >= 1: # type: ignore
                fs.append(int(x["Level"])) # type: ignore
            else:
                fs.append(0)
    try:
        wcs = equip_data[11]["ColorStone"]["Name"] # type: ignore
        wcs_icon = equip_data[11]["ColorStone"]["Icon"]["FileName"] # type: ignore
    except Exception as _:
        wcs = ""
        wcs_icon = ""
    try:
        wcs1 = equip_data[12]["ColorStone"]["Name"] # type: ignore
        wcs_icon1 = equip_data[12]["ColorStone"]["Icon"]["FileName"] # type: ignore
    except Exception as _:
        wcs1 = ""
        wcs_icon1 = ""
    values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    if flag == 1:
        panel = data["matchDetail"]
        for i in list(panel):
            if i == "totalAttack":
                values[0] = str(panel[i]) # type: ignore
            if i == "baseAttack":
                values[1] = str(panel[i]) # type: ignore
            if i == "atCriticalStrikeLevel": 
                values[2] = str(panel[i]) + "%" # type: ignore
            if i == "atCriticalDamagePowerBaseLevel":
                values[3] = str(panel[i]) + "%" # type: ignore
            if i == "atHasteBaseLevel":
                values[4] = str(panel[i]) # type: ignore
            if i == att_mapping(att):
                values[5] = str(panel[i]) # type: ignore
            if i == "atOvercomeBaseLevel":
                values[6] = str(panel[i]) + "%" # type: ignore
            if i == "atStrainBaseLevel":
                values[7] = str(panel[i]) + "%" # type: ignore
            if i == "atSurplusValueBase":
                values[8] = str(panel[i]) # type: ignore
            if i == "totalLift":
                values[9] = str(panel[i]) # type: ignore
            if i == "atToughnessBaseLevel": 
                values[10] = str(panel[i]) + "%" # type: ignore
            if i == "atDecriticalDamagePowerBaseLevel":
                values[11] = str(panel[i]) + "%" # type: ignore
    elif flag == 2:
        panel = data["matchDetail"]
        for i in list(panel):
            if i == "totaltherapyPowerBase":
                values[0] = str(panel[i]) # type: ignore
            if i == "therapyPowerBase":
                values[1] = str(panel[i]) # type: ignore
            if i == "atCriticalStrikeLevel":
                values[2] = str(panel[i]) + "%" # type: ignore
            if i == "atCriticalDamagePowerBaseLevel":
                values[3] = str(panel[i]) + "%" # type: ignore
            if i == "atHasteBaseLevel":
                values[4] = str(panel[i]) # type: ignore
            if i == "atSpiritBase":
                values[5] = str(panel[i]) # type: ignore
            if i == "atPhysicsShieldBaseLevel":
                values[6] = str(panel[i]) + "%" # type: ignore
            if i == "atMagicShieldLevel":
                values[7] = str(panel[i]) + "%" # type: ignore
            if i == "atSurplusValueBase":
                values[8] = str(panel[i]) # type: ignore
            if i == "totalLift":
                values[9] = str(panel[i]) # type: ignore
            if i == "atToughnessBaseLevel":
                values[10] = str(panel[i]) + "%" # type: ignore
            if i == "atDecriticalDamagePowerBaseLevel":
                values[11] = str(panel[i]) + "%" # type: ignore
    else:
        panel = data["matchDetail"]
        for i in list(panel):
            if i == "atPhysicsShieldBaseLevel":
                values[0] = str(panel[i]) + "%" # type: ignore
            if i == "atMagicShieldLevel": 
                values[1] = str(panel[i]) + "%" # type: ignore
            if i == "totalLift":
                values[2] = str(panel[i]) # type: ignore
            if i == "atSurplusValueBase":
                values[3] = str(panel[i]) # type: ignore
            if i == "atToughnessBaseLevel":
                values[4] = str(panel[i]) + "%" # type: ignore
            if i == "atDodgeLevel":
                values[5] = str(panel[i]) + "%" # type: ignore
            if i == "atParryBaseLevel":
                values[6] = str(panel[i]) + "%" # type: ignore
            if i == "atParryValue":
                values[7] = str(panel[i]) # type: ignore
            if i == "atVitalityBase":
                values[8] = str(panel[i]) # type: ignore
            if i == "atStrainBaseLevel":
                values[10] = str(panel[i]) + "%" # type: ignore
            if i == "atHasteBaseLevel":
                values[11] = str(panel[i]) # type: ignore
                values[9] = "%.2f%%" % (panel[i]/96483.75 * 100)
    img = await get_attr(kf, maxjl_list, jl_list, equip_list, equip_icon_list, equip_quailty, basic, henchant, lenchant, fs, wcs_icon, wcs, values, wcs1, wcs_icon1)
    return img


async def get_attr(kungfu: str, maxjl_list: list, jl_list: list, equip_list: list, equip_icon_list: list, equip_quailty: list, basic: list, henchant: list, lenchant: list, fs: list, wcs_icon: str, wcs: str, attrs: list, wcs1, wcs_icon1):
    attr = kungfu_mapping(kungfu)
    syst_bold = ASSETS + "/font/syst-bold.ttf"
    syst_mid = ASSETS + "/font/syst-mid.ttf"
    msyh = ASSETS + "/font/msyh.ttf"
    calibri = ASSETS + "/font/calibri.ttf"
    if attr in ["根骨", "元气", "力道", "身法"]:
        objects = ["面板攻击", "基础攻击", "会心", "会心效果", "加速", attr, "破防", "无双", "破招", "最大气血值", "御劲", "化劲"]
    elif attr == "治疗":
        objects = ["面板治疗量", "基础治疗量", "会心", "会心效果", "加速",
                   "根骨", "外防", "内防", "破招", "最大气血值", "御劲", "化劲"]
    elif attr == "防御":
        objects = ["外防", "内防", "最大气血值", "破招", "御劲", "闪避", "招架", "拆招", "体质", "加速率", "无双", "加速"]
    else:
        raise ValueError("Unknown type of kungfu!")
    background = Image.open(await get_bg(kungfu_to_school(kungfu)))
    draw = ImageDraw.Draw(background)
    flickering = Image.open(PLUGINS + "/jx3/attributes/flicker.png").resize((38, 38))
    precious = Image.open(PLUGINS + "/jx3/attributes/xy.png")
    full_jinglian = Image.open(PLUGINS + "/jx3/attributes/jl.png")
    un_full_jinglian = Image.open(PLUGINS + "/jx3/attributes/unjl.png")
    heavy_enchant = Image.open(PLUGINS + "/jx3/attributes/henchant.png").resize((20, 20))
    little_enchant = Image.open(PLUGINS + "/jx3/attributes/lenchant.png").resize((20, 20))

    # 心法图标
    background.alpha_composite(Image.open(await get_kf_icon(kungfu)).resize((50, 50)), (61, 62))

    # 武器图标
    if kungfu not in ["问水诀", "山居剑意"]:
        if equip_icon_list[11] != "":
            if judge_special_weapon(equip_list[11]):
                background.alpha_composite(precious, (688, 586))
            background.alpha_composite(Image.open(await local_save(equip_icon_list[11])).resize((38, 38)), (708, 587))
            if maxjl_list[11] in ["3", "4", "8"]:
                background.alpha_composite(precious, (688, 586))
                if maxjl_list[11] == "8":
                    background.alpha_composite(flickering, (707, 586))
                else:
                    if maxjl_list[11] == jl_list[11]:
                        background.alpha_composite(full_jinglian, (708, 587))
            else:
                if maxjl_list[11] == jl_list[11]:
                    background.alpha_composite(full_jinglian, (708, 587))
                else:
                    background.alpha_composite(un_full_jinglian, (708, 587))
    else:
        if equip_icon_list[11] != "":
            if judge_special_weapon(equip_list[11]):
                background.alpha_composite(precious, (688, 586))
            background.alpha_composite(Image.open(await local_save(equip_icon_list[11])).resize((38, 38)), (708, 587))
            if maxjl_list[11] in ["3", "4", "8"]:
                background.alpha_composite(precious, (688, 586))
                if maxjl_list[11] == "8":
                    background.alpha_composite(flickering, (708, 587))
                else:
                    if maxjl_list[11] == jl_list[11]:
                        background.alpha_composite(full_jinglian, (708, 587))
            else:
                if maxjl_list[11] == jl_list[11]:
                    background.alpha_composite(full_jinglian, (708, 587))
                else:
                    background.alpha_composite(un_full_jinglian, (708, 587))
        if equip_icon_list[12] != "":
            if judge_special_weapon(equip_list[12]):
                background.alpha_composite(precious, (688, 635))
            background.alpha_composite(Image.open(await local_save(equip_icon_list[12])).resize((38, 38)), (708, 636))
            if maxjl_list[12] in ["3", "4", "8"]:
                background.alpha_composite(precious, (688, 635))
                if maxjl_list[12] == "8":
                    background.alpha_composite(flickering, (708, 636))
                else:
                    if maxjl_list[12] == jl_list[12]:
                        background.alpha_composite(full_jinglian, (708, 636))
            else:
                if maxjl_list[12] == jl_list[12]:
                    background.alpha_composite(full_jinglian, (708, 636))
                else:
                    background.alpha_composite(un_full_jinglian, (708, 636))

    # 装备图标
    init = 48
    limit = 0
    for i in equip_icon_list:
        if i != "":
            background.alpha_composite(Image.open(await local_save(i)).resize((38, 38)), (708, init))
        init = init + 49
        limit = limit + 1
        if limit == 11:
            break

    # 装备精炼
    init = 47
    range_time = 11
    if kungfu in ["问水诀", "山居剑意"]:
        range_time = range_time + 1
    for i in range(range_time):
        if judge_special_weapon(equip_list[i]):
            background.alpha_composite(precious, (687, init - 1))
        if maxjl_list[i] in ["3", "4", "8"]:
            background.alpha_composite(precious, (687, init - 1))
        if jl_list[i] == maxjl_list[i]:
            background.alpha_composite(full_jinglian, (707, init))
        else:
            if equip_list[i] != "":
                background.alpha_composite(un_full_jinglian, (707, init))
        if maxjl_list[i] == "8":
            background.alpha_composite(flickering, (709, init + 2))
        init = init + 49

    # 装备名称
    init = 50
    for i in equip_list:
        if i != "":
            draw.text((752, init), i, fill=(255, 255, 255),
                      font=ImageFont.truetype(syst_bold, size=14), anchor="lt")
        init = init + 49

    # 装备品级 + 属性
    init = 71
    for i in equip_quailty:
        if i != "":
            draw.text((752, init), i, fill=(255, 255, 255),
                      font=ImageFont.truetype(syst_bold, size=14), anchor="lt")
        init = init + 49

    # 个人基本信息
    draw.text((85, 127), str(basic[0]), fill=(0, 0, 0),
              font=ImageFont.truetype(calibri, size=18), anchor="mt")
    draw.text((370, 70), basic[1], fill=(255, 255, 255),
              font=ImageFont.truetype(msyh, size=32), anchor="mm")
    draw.text((370, 120), basic[2], fill=(255, 255, 255),
              font=ImageFont.truetype(msyh, size=20), anchor="mm")
    draw.text((450, 120), basic[3], fill=(127, 127, 127),
              font=ImageFont.truetype(calibri, size=18), anchor="mm")

    # 面板内容
    positions = [(127, 226), (258, 226), (385, 226), (514, 226), (127, 303), (258, 303),
                 (385, 303), (514, 303), (127, 380), (258, 380), (385, 380), (514, 380)]
    range_time = 12
    for i in range(range_time):
        draw.text(positions[i], objects[i], fill=(255, 255, 255),
                  font=ImageFont.truetype(syst_bold, size=20), anchor="mm")

    # 面板数值
    draw.text((129, 201), attrs[0], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((258, 201), attrs[1], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((385, 201), attrs[2], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((514, 201), attrs[3], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((129, 278), attrs[4], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((258, 278), attrs[5], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((385, 278), attrs[6], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((514, 278), attrs[7], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((129, 355), attrs[8], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((258, 355), attrs[9], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((385, 355), attrs[10], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    draw.text((514, 355), attrs[11], fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")

    # 装备位置
    init = 50
    equips = ["帽子", "上衣", "腰带", "护手", "下装", "鞋子", "项链", "腰坠", "戒指", "戒指", "远程武器", "近身武器"]
    for i in equips:
        draw.text((940, init), i, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="lt")
        init = init + 49

    # 五行石
    positions = [(940, 65), (960, 65), (940, 114), (960, 114), (940, 163), (960, 163), (940, 212), (960, 212), (940, 261),
                 (960, 261), (940, 310), (960, 310), (940, 359), (940, 408), (940, 604), (940, 555), (960, 604), (980, 604)]
    range_time = 18
    if kungfu in ["问水诀", "山居剑意"]:
        range_time = range_time + 3
        positions.append((940, 653))
        positions.append((960, 653))
        positions.append((980, 653))
    for i in range(range_time):
        background.alpha_composite(Image.open(get_fs(fs[i])).resize((20, 20)), positions[i])

    # 小附魔
    init = 45
    for i in lenchant:
        if i == "":
            init = init + 49
            continue
        else:
            background.alpha_composite(little_enchant, (1044, init))
            draw.text((1068, init + 4), i, file=(255, 255, 255),
                      font=ImageFont.truetype(msyh, size=12), anchor="lt")
            init = init + 49

    # 大附魔
    y = [65, 114, 163, 212, 310]
    for i in range(5):
        if henchant[i] == "":
            continue
        else:
            background.alpha_composite(heavy_enchant, (1044, y[i]))
            draw.text((1068, y[i] + 4), henchant[i], file=(255, 255, 255),
                      font=ImageFont.truetype(msyh, size=12), anchor="lt")

    # 五彩石
    if wcs_icon != "":
        background.alpha_composite(Image.open(await local_save(wcs_icon)).resize((20, 20)), (1044, 604))
    if wcs != "":
        draw.text((1068, 608), wcs, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="lt")
    if wcs_icon1 != "":
        background.alpha_composite(Image.open(await local_save(wcs_icon1)).resize((20, 20)), (1044, 654))
    if wcs1 != "":
        draw.text((1068, 657), wcs1, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="lt")

    final_path = CACHE + "/" + get_uuid() + ".png"
    background.save(final_path)
    return final_path
