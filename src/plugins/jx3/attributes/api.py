from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from src.constant.jx3.skilldatalib import kftosh

from src.tools.basic.msg import PROMPT
from src.tools.generate import get_uuid
from src.tools.config import Config
from src.tools.utils.request import get_api, get_content, post_url
from src.tools.basic.data_server import server_mapping, Zone_mapping
from src.tools.file import read
from src.tools.utils.path import ASSETS, CACHE, PLUGINS
from src.tools.basic.jx3 import gen_ts, format_body, gen_xsk

from src.plugins.jx3.bind import get_player_local_data

import os
import json

bot_name = Config.bot_basic.bot_name_argument
token = Config.jx3.api.token
ticket = Config.jx3.api.ticket
device_id = ticket.split("::")[-1]

async def get_uid(server, id):
    token = Config.jx3.api.token
    data = await get_player_local_data(role_name=id, server_name=server)
    data = data.format_jx3api()
    if data["code"] != 200:
        return False
    else:
        return [data["data"]["roleId"], data["data"]["bodyName"], data["data"]["forceName"]]


async def get_personal_kf(kfid):
    kfdt = json.loads(read(PLUGINS + "/jx3/attributes/schoolmapping.json"))
    for i in list(kfdt):
        if str(kfdt[i]) == str(kfid):
            return i
    return False


def find_qx(data, kf, qx):
    kfdt = json.loads(read(PLUGINS + "/jx3/attributes/schoolmapping.json"))
    if kf not in kfdt:
        return None
    if qx == "蒹山":
        qx = "兼山"
    if qx == "桑拓":
        qx = "桑柘"
    if qx.find("素矰") != -1:
        qx = "素矰"
    real_data = data[kf]
    for i in range(1, 13):
        for x in range(1, 6):
            try:
                each = real_data[str(i)][str(x)]
            except:
                continue
            if each["name"] == qx:
                return i-1


def data_process(kf, data, f):
    final = ["", "", "", "", "", "", "", "", "", "", "", ""]
    if kf in ["问水诀", "山居剑意"]:
        final.append("")
    flag = False
    if f:
        data = data["data"]
    for i in data["Equips"]:
        if i["Icon"]["SubKind"] == "帽子":
            final[0] = i
        if i["Icon"]["SubKind"] == "上衣":
            final[1] = i
        if i["Icon"]["SubKind"] == "腰带":
            final[2] = i
        if i["Icon"]["SubKind"] == "护臂":
            final[3] = i
        if i["Icon"]["SubKind"] == "裤子":
            final[4] = i
        if i["Icon"]["SubKind"] == "鞋":
            final[5] = i
        if i["Icon"]["SubKind"] == "项链":
            final[6] = i
        if i["Icon"]["SubKind"] == "腰坠":
            final[7] = i
        if i["Icon"]["SubKind"] == "戒指":
            if flag:
                final[9] = i
                continue
            final[8] = i
            flag = True
            continue
        if i["Icon"]["SubKind"] in "投掷囊":
            final[10] = i
        if i["Icon"]["SubKind"] != "投掷囊" and i["Icon"]["SubKind"] != "重剑" and (i["Icon"]["Kind"] == "武器" or (i["Icon"]["Kind"] == "任务特殊" and i["Icon"]["SubKind"] == "活动相关")): 
            final[11] = i
        if i["Icon"]["SubKind"] == "重剑":
            final[12] = i
    return final


def enchant_mapping(quailty):
    data = {
        "天堑奇珵": {
            "min": 14350,
            "max": 15800
        },
        "天堑奇玿": {
            "min": 12800,
            "max": 14150
        },
        "天堑奇瑛": {
            "min": 11500,
            "max": 12600
        },
        "天堑奇珂": {
            "min": 10600,
            "max": 11300
        },
        "天堑奇琨": {
            "min": 9800,
            "max": 10300
        },
        "山市鬼洲": {
            "min": 6500,
            "max": 7200
        },
        "山市鬼域": {
            "min": 5850,
            "max": 6450
        },
        "山市鬼船": {
            "min": 5250,
            "max": 5800
        },
        "山市鬼冢": {
            "min": 4750,
            "max": 5200
        },
        "山市鬼楼": {
            "min": 4400,
            "max": 4700
        },
        "昆吾焰珩": {
            "min": 2900,
            "max": 3300
        },
        "昆吾焰珀": {
            "min": 2750,
            "max": 2950
        },
        "昆吾焰砂": {
            "min": 2300,
            "max": 2450
        },
        "昆吾焰晶": {
            "min": 2500,
            "max": 2700
        }
    }
    for i in list(data):
        max_ = data[i]["max"]
        min_ = data[i]["min"]
        if min_ <= int(quailty) <= max_:
            return i


def get_fs(level: int):
    return ASSETS + "/wuxingshi/" + str(level) + ".png"


async def get_bg(sc):
    final_path = ASSETS + "/jx3/bg/" + sc + ".png"
    if os.path.exists(final_path):
        return final_path
    else:
        data = await get_content(f"https://cdn.jx3box.com/static/pz/img/overview/horizontal/{sc}.png")
        with open(final_path, mode="wb") as cache:
            cache.write(data)
        return final_path


async def get_kf_icon(kf):
    school_mapping = json.loads(read(PLUGINS + "/jx3/attributes/schoolmapping.json"))
    flag = False
    try:
        num = school_mapping[kf]
    except:
        flag = True
    final_path = ASSETS + "/jx3/kungfu/" + kf + ".png"
    if os.path.exists(final_path):
        return final_path
    else:
        if not flag:
            data = await get_content(f"https://img.jx3box.com/image/xf/{num}.png")
        else:
            data = await get_content("https://img.jx3box.com/image/xf/0.png")
        with open(final_path, mode="wb") as cache:
            cache.write(data)
        return final_path


def kungfu_mapping(kf):
    if kf in ["紫霞功", "莫问", "毒经", "无方", "冰心诀"]:
        return "根骨"
    elif kf in ["花间游", "易筋经", "焚影圣诀", "太玄经", "天罗诡道"]:
        return "元气"
    elif kf in ["太虚剑意", "问水诀", "山居剑意", "凌海诀", "隐龙诀", "分山劲", "山海心诀"]:
        return "身法"
    elif kf in ["傲血战意", "惊羽诀", "北傲诀", "孤锋诀", "笑尘诀"]:
        return "力道"
    elif kf in ["相知", "离经易道", "灵素", "补天诀", "云裳心经"]:
        return "治疗"
    elif kf in ["铁牢律", "铁骨衣", "明尊琉璃体", "洗髓经"]:
        return "防御"
    else:
        return False


async def get_attr_main(server, id, group_id):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    uid = await get_uid(server, id)
    if not uid:
        return [f"唔……未找到该玩家，请提交角色！\n提交角色 服务器 UID"]
    param = {
        "zone": Zone_mapping(server),
        "server": server,
        "game_role_id": uid[0],
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
    data = json.loads(data)
    kfid = data["data"]["Kungfu"]["KungfuID"]
    kf = await get_personal_kf(kfid)
    if not kf:
        kf = uid[2]
    kf = kf.replace("决", "诀")
    if kf == "山居剑意":
        kf = "问水诀"
    att = kungfu_mapping(kf)
    if att in ["根骨", "元气", "力道", "身法"]:
        flag = 1
    elif att == "治疗":
        flag = 2
    elif att == "防御":
        flag = 3
    else:
        flag = 4
    try:
        school_body = uid[2] + "·" + uid[1]
    except:
        return ["门派、体型等关键数据缺失，请尝试使用旗舰端在世界频道发言！"]
    uid = uid[0]
    equip_data = data_process(kf, data, True)
    maxjl_list = []
    jl_list = []
    equip_list = []
    equip_icon_list = []
    equip_quailty = []
    score = data["data"]["TotalEquipsScore"]
    basic = [score, id, school_body, uid]
    messyqx = []
    for i in data["data"]["Person"]["qixueList"]:
        messyqx.append(i["name"])
    qx = ["未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知"]
    unknown = PLUGINS + "/jx3/attributes/unknown.png"
    qx_icon = [unknown, unknown, unknown, unknown, unknown, unknown,
               unknown, unknown, unknown, unknown, unknown, unknown]
    henchant = ["", "", "", "", "", ""]
    lenchant = ["", "", "", "", "", "", "", "", "", "", "", ""]
    if kf in ["问水诀", "山居剑意"]:
        lenchant.append("")
    versions = await get_api("https://data.jx3box.com/talent/index.json")
    for i in versions:
        if i["name"].find("体服") != -1:
            continue
        else:
            ver = i["version"]
            break
    qxdata = await get_api(f"https://data.jx3box.com/talent/{ver}.json")
    for i in messyqx:
        index = find_qx(qxdata, kf, i)
        if index == None:
            continue
        qx[index] = i
    for i in range(12):
        for x in data["data"]["Person"]["qixueList"]:
            qx_name = x["name"].replace(" ", "")
            if qx_name == qx[i]:
                qx_icon[i] = x["icon"]["FileName"]
    for i in equip_data:
        if i == "":
            equip_quailty.append("")
        else:
            msg = i["Quality"]
            try:
                modify = i["ModifyType"]
            except:
                equip_quailty.append(msg)
                continue
            for x in modify:
                content = x["Attrib"]["GeneratedMagic"].split("提高")
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
            equip_icon_list.append(unknown)
        else:
            maxjl_list.append(i["MaxStrengthLevel"])
            jl_list.append(i["StrengthLevel"])
            equip_list.append(i["Name"] + "(" + i["StrengthLevel"] +
                              "/" + i["MaxStrengthLevel"] + ")")
            equip_icon_list.append(i["Icon"]["FileName"])
    for i in equip_data:
        if i == "":
            if equip_data.index(i) in [0, 1, 2, 3, 5]:
                henchant[equip_data.index(i)] = ""
                continue
        try:
            i["Icon"]["SubKind"]
        except:
            if equip_data.index(i) in [0, 1, 2, 3, 5]:
                henchant[equip_data.index(i)] = ""
                continue
        if type(i) != type({}):
            continue
        if i["Icon"]["SubKind"] == "帽子":
            if "WCommonEnchant" in list(i):
                attrs_ = json.dumps(i["ModifyType"], ensure_ascii=False)
                if attrs_.find("攻击") != -1:
                    type_ = "伤"
                elif attrs_.find("治疗") != -1:
                    type_ = "疗"
                else:
                    type_ = "御"
                name = enchant_mapping(i["Quality"]) + "·" + type_ + "·帽"
                henchant[0] = name
            else:
                henchant[0] = ""
        elif i["Icon"]["SubKind"] == "上衣":
            if "WCommonEnchant" in list(i):
                attrs_ = json.dumps(i["ModifyType"], ensure_ascii=False)
                if attrs_.find("攻击") != -1:
                    type_ = "伤"
                elif attrs_.find("治疗") != -1:
                    type_ = "疗"
                else:
                    type_ = "御"
                name = enchant_mapping(i["Quality"]) + "·" + type_ + "·衣"
                henchant[1] = name
            else:
                henchant[1] = ""
        elif i["Icon"]["SubKind"] == "腰带":
            if "WCommonEnchant" in list(i):
                attrs_ = json.dumps(i["ModifyType"], ensure_ascii=False)
                if attrs_.find("攻击") != -1:
                    type_ = "伤"
                elif attrs_.find("治疗") != -1:
                    type_ = "疗"
                else:
                    type_ = "御"
                name = enchant_mapping(i["Quality"]) + "·" + type_ + "·腰"
                henchant[2] = name
            else:
                henchant[2] = ""
        elif i["Icon"]["SubKind"] == "护臂":
            if "WCommonEnchant" in list(i):
                attrs_ = json.dumps(i["ModifyType"], ensure_ascii=False)
                if attrs_.find("攻击") != -1:
                    type_ = "伤"
                elif attrs_.find("治疗") != -1:
                    type_ = "疗"
                else:
                    type_ = "御"
                name = enchant_mapping(i["Quality"]) + "·" + type_ + "·腕"
                henchant[3] = name
            else:
                henchant[3] = ""
        elif i["Icon"]["SubKind"] == "鞋":
            if "WCommonEnchant" in list(i):
                attrs_ = json.dumps(i["ModifyType"], ensure_ascii=False)
                if attrs_.find("攻击") != -1:
                    type_ = "伤"
                elif attrs_.find("治疗") != -1:
                    type_ = "疗"
                else:
                    type_ = "御"
                name = enchant_mapping(i["Quality"]) + "·" + type_ + "·鞋"
                henchant[4] = name
            else:
                henchant[4] = ""
    num = 0
    for i in equip_data:
        if i != "":
            if "WPermanentEnchant" in list(i):
                lenchant[num] = i["WPermanentEnchant"]["Name"]
                num = num + 1
            else:
                num = num + 1
                continue
        else:
            num = num + 1
            continue
    fs = []
    num = 0
    for i in equip_data:
        num = num + 1
        if i == "" and num in [7, 8, 11]:
            fs.append(0)
            continue
        elif i == "" and num in [1, 2, 3, 4, 5, 6]:
            fs.append(0)
            fs.append(0)
            continue
        elif i == "" and num in [12, 13]:
            fs.append(0)
            fs.append(0)
            fs.append(0)
            continue
        try:
            i["FiveStone"]
        except:
            continue
        for x in i["FiveStone"]:
            if x["Name"] != "":
                fs.append(int(x["Level"]))
            else:
                fs.append(0)
    try:
        wcs = equip_data[11]["ColorStone"]["Name"]
        wcs_icon = equip_data[11]["ColorStone"]["Icon"]["FileName"]
    except:
        wcs = ""
        wcs_icon = ""
    try:
        wcs1 = equip_data[12]["ColorStone"]["Name"]
        wcs_icon1 = equip_data[12]["ColorStone"]["Icon"]["FileName"]
    except:
        wcs1 = ""
        wcs_icon1 = ""
    values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    if flag == 1:
        panel = data["data"]["PersonalPanel"]
        for i in panel:
            if i["name"] == "攻击力":
                values[0] = str(i["value"])
            if i["name"] == "基础攻击力":
                values[1] = str(i["value"])
            if i["name"] == "会心":
                values[2] = str(i["value"]) + "%"
            if i["name"] == "会心效果":
                values[3] = str(i["value"]) + "%"
            if i["name"] == "加速":
                values[4] = str(i["value"])
            if i["name"] == att:
                values[5] = str(i["value"])
            if i["name"] == "破防":
                values[6] = str(i["value"]) + "%"
            if i["name"] == "无双":
                values[7] = str(i["value"]) + "%"
            if i["name"] == "破招":
                values[8] = str(i["value"])
            if i["name"] == "气血":
                values[9] = str(i["value"])
            if i["name"] == "御劲":
                values[10] = str(i["value"]) + "%"
            if i["name"] == "化劲":
                values[11] = str(i["value"]) + "%"
    elif flag == 2:
        panel = data["data"]["PersonalPanel"]
        for i in panel:
            if i["name"] == "治疗量":
                values[0] = str(i["value"])
            if i["name"] == "治疗量":
                values[1] = str(i["value"])
            if i["name"] == "会心":
                values[2] = str(i["value"]) + "%"
            if i["name"] == "会心效果":
                values[3] = str(i["value"]) + "%"
            if i["name"] == "加速":
                values[4] = str(i["value"])
            if i["name"] == "根骨":
                values[5] = str(i["value"])
            if i["name"] == "外功防御":
                values[6] = str(i["value"]) + "%"
            if i["name"] == "内功防御":
                values[7] = str(i["value"]) + "%"
            if i["name"] == "破招":
                values[8] = str(i["value"])
            if i["name"] == "气血":
                values[9] = str(i["value"])
            if i["name"] == "御劲":
                values[10] = str(i["value"]) + "%"
            if i["name"] == "化劲":
                values[11] = str(i["value"]) + "%"
    elif flag == 3:
        panel = data["data"]["PersonalPanel"]
        for i in panel:
            if i["name"] == "外功防御":
                values[0] = str(i["value"]) + "%"
            if i["name"] == "内功防御":
                values[1] = str(i["value"]) + "%"
            if i["name"] == "气血":
                values[2] = str(i["value"])
            if i["name"] == "破招":
                values[3] = str(i["value"])
            if i["name"] == "御劲":
                values[4] = str(i["value"]) + "%"
            if i["name"] == "闪避":
                values[5] = str(i["value"]) + "%"
            if i["name"] == "招架":
                values[6] = str(i["value"]) + "%"
            if i["name"] == "拆招":
                values[7] = str(i["value"])
            if i["name"] == "体质":
                values[8] = str(i["value"])
            if i["name"] == "无双":
                values[10] = str(i["value"]) + "%"
            if i["name"] == "加速":
                values[11] = str(i["value"])
                values[9] = "%.2f%%" % (i["value"]/96483.75 * 100)
    else:
        values = ["未知属性", "未知属性", "未知属性", "未知属性", "未知属性", "未知属性", "未知属性", "未知属性", "未知属性", "未知属性", "未知属性", "未知属性"]
    img = await get_attr(kf, maxjl_list, jl_list, equip_list, equip_icon_list, equip_quailty, basic, qx, qx_icon, henchant, lenchant, fs, wcs_icon, wcs, values, wcs1, wcs_icon1)
    return img


async def local_save(webpath):
    file_name = webpath.split("/")[-1].split("?")[0]
    if webpath.find("unknown.png") != -1:
        return PLUGINS + "/jx3/attributes/unknown.png"
    final_path = ASSETS + "/jx3/kungfu/" + file_name + ".png"
    if os.path.exists(final_path):
        return final_path
    else:
        try:
            main = await get_content(webpath)
        except:
            return webpath
        with open(final_path, mode="wb") as cache:
            cache.write(main)
        return final_path


def judge_special_weapon(name):
    special_weapons = ["雪凤冰王笛", "血影天宇舞姬", "炎枪重黎", "腾空", "画影", "金刚", "岚尘金蛇", "苌弘化碧", "蝎心忘情", "抱朴狩天", "八相连珠", "圆月双角", "九龙升景", "斩马刑天", "风雷瑶琴剑", "五相斩", "雪海散华", "麒王逐魂"]
    for i in special_weapons:
        if name.split("(")[0] in special_weapons:
            return True
    return False


async def get_attr(kungfu: str, maxjl_list: list, jl_list: list, equip_list: list, equip_icon_list: list, equip_quailty: list, basic: list, qx: list, qx_icon: list, henchant: list, lenchant: list, fs: list, wcs_icon: str, wcs: str, attrs: list, wcs1, wcs_icon1):
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
        objects = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    background = Image.open(await get_bg(kftosh(kungfu)))
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

    # 奇穴
    draw.text((320, 435), "奇穴", fill=(255, 255, 255),
              font=ImageFont.truetype(syst_mid, size=20), anchor="mm")
    init = 179
    limit = 0
    y = 479
    done_time = 0
    for i in qx_icon:
        qximg = Image.open(await local_save(i)).resize((39, 39))
        background.alpha_composite(qximg, (init, y))
        init = init + 48
        limit = limit + 1
        if limit == 6:
            limit = 0
            init = 179
            y = 547
            done_time = done_time + 1
            if done_time == 2:
                break

    init = 199
    y = 530
    limit = 0
    done_time = 0
    for i in qx:
        draw.text((init, y), i, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="mm")
        init = init + 48
        limit = limit + 1
        if limit == 6:
            limit = 0
            init = 199
            y = 598
            done_time = done_time + 1
            if done_time == 2:
                break

    # 装备位置
    init = 50
    equips = ["帽子", "上衣", "腰带", "护手", "下装", "鞋子", "项链", "腰坠", "戒指", "戒指", "远程武器", "近身武器"]
    for i in equips:
        draw.text((940, init), i, file=(255, 255, 255),
                  font=ImageFont.truetype(msyh, size=12), anchor="lt")
        init = init + 49

    # 五行石
    positions = [(940, 65), (960, 65), (940, 114), (960, 114), (940, 163), (960, 163), (940, 212), (960, 212), (940, 261),
                 (960, 261), (940, 310), (960, 310), (940, 359), (940, 408), (940, 555), (940, 604), (960, 604), (980, 604)]
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
    return Path(final_path).as_uri()