from pathlib import Path

from nonebot.log import logger
from src.tools.generate import generate, get_uuid
from src.tools.basic.data_server import server_mapping
from src.tools.config import Config
from src.tools.utils.request import get_api, post_url
from src.tools.basic.jx3 import gen_ts, gen_xsk, format_body, dungeon_sign
from src.tools.utils.path import ASSETS, CACHE, PLUGINS, VIEWS
from src.tools.utils.common import convert_time, getCurrentTime, getRelateTime
from src.tools.file import read, write

from src.plugins.jx3.bind import get_player_local_data
from src.plugins.jx3.attributes import Zone_mapping

import json
import re
import time

token = Config.jx3.api.token
ticket = Config.jx3.api.ticket
bot_name = Config.bot_basic.bot_name_argument
device_id = ticket.split("::")[-1]

async def get_cd(server: str, sep: str):
    url = f"https://pull.j3cx.com/api/serendipity?server={server}&serendipity={sep}&pageSize=1"
    data = await get_api(url)
    data = data.get("data").get("data")
    if not data:
        return "没有记录哦~"
    data = data[0]
    time = data["date_str"]
    msg = f"「{server}」服务器上一次记录「{sep}」：\n{time}\n数据来源：@茗伊插件集"
    return msg

async def get_map(name, mode):
    param = {
        "mode": 2,
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
    data = await post_url(url="https://m.pvp.xoyo.com/dungeon/list", data=param, headers=headers)
    data = json.loads(data)
    for i in data["data"]:
        for x in i["dungeon_infos"]:
            if x["name"] == name:
                for y in x["maps"]:
                    if y["mode"] == mode:
                        return y["map_id"]


async def get_boss(map, mode, boss):
    map_id = await get_map(map, mode)
    param = {
        "map_id": map_id,
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
    data = await post_url(url="https://m.pvp.xoyo.com/dungeon/info", data=param, headers=headers)
    data = json.loads(data)
    for i in data["data"]["info"]["boss_infos"]:
        if i["name"] == boss:
            return i["index"]


async def get_drops(map, mode, boss):
    boss_id = await get_boss(map, mode, boss)
    param = {
        "boss_id": boss_id,
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
    data = await post_url(url="https://m.pvp.xoyo.com/dungeon/boss-drop", data=param, headers=headers)
    return json.loads(data)

# 暂时不打算做5人副本，5人副本与10人副本的请求地址不同。
# 10人/25人：https://m.pvp.xoyo.com/dungeon/list
# 5人：https://m.pvp.xoyo.com/dungeon/list-all
# 暂时未知数据是否相同，后续考虑是否添加。

def mode_mapping(mode):
    with open(PLUGINS + "/jx3/dungeon/mode.json", "r", encoding="utf-8") as f:
        mode_mapping_dict = json.load(f)

    for k, v in mode_mapping_dict.items():
        if mode in v:
            return k
    return False

def zone_mapping(zone):
    with open(PLUGINS + "/jx3/dungeon/zone.json", "r", encoding="utf-8") as f:
        zone_mapping_dict = json.load(f)

    for k, v in zone_mapping_dict.items():
        if zone in v:
            return k
    return False


star = """
<svg width="20" height="20">
    <polygon points="10,0 13,7 20,7 14,12 16,19 10,15 4,19 6,12 0,7 7,7" style="fill:gold; stroke:gold; stroke-width:1px;" />
</svg>
"""

template_drop = """
<tr>
    <td class="short-column">
        <img src="$icon"></img>
    </td>
    <td class="short-column">$name</td>
    <td class="short-column">
        <div class="attrs">$attrs</div></td>
    <td class="short-column">$type</td>
    <td class="short-column">
        $stars
    </td>
    <td class="short-column">$quailty</td>
    <td class="short-column">$score</td>
    <td class="short-column"><div class="attrs">$fivestone</div></td>
</tr>
"""

equip_types = ["帽子", "上衣", "腰带", "护臂", "裤子", "鞋", "项链", "腰坠", "戒指", "投掷囊"]

filter_words = ["根骨", "力道", "元气", "身法", "体质"]


async def generater(map, mode, boss):
    mode = mode_mapping(mode)
    if mode is False:
        return [f"唔……难度似乎{Config.bot_basic.bot_name}不能理解哦~"]
    zone = zone_mapping(map)
    if zone is False:
        return [f"唔……副本名称似乎{Config.bot_basic.bot_name}不能理解哦~"]
    try:
        data = await get_drops(zone, mode, boss)
    except KeyError:
        return ["唔……没有找到该掉落列表，请检查副本名称、BOSS名称或难度~"]
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
        return ["唔……没有找到该boss的掉落哦~\n您确定" + f"{boss}住在{mode}{map}吗？"]
    else:
        tablecontent = []
        for i in armors:
            name = i["Name"]
            icon = i["Icon"]["FileName"]
            if i["Icon"]["SubKind"] in equip_types:
                if "Type" in list(i):
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
                    attrs_data = i["ModifyType"]
                    attrs_list = []
                    for x in attrs_data:
                        string = x["Attrib"]["GeneratedMagic"]
                        flag = False
                        for y in filter_words:
                            if string.find(y) != -1:
                                flag = True
                        if flag:
                            continue
                        attrs_list.append(string)
                    attrs = "<br>".join(attrs_list)
                    if i["Icon"]["SubKind"] != "戒指":
                        diamon_data = i["DiamonAttribute"]
                        diamon_list = []
                        logger.info(diamon_data)
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
            tablecontent.append(template_drop.replace("$icon", icon).replace("$name", name).replace("$attrs", attrs).replace(
                "$type", type_).replace("$stars", stars).replace("$quailty", quailty).replace("$score", score).replace("$fivestone", fivestone))
        for i in weapons:
            name = i["Name"]
            icon = i["Icon"]["FileName"]
            type_ = i["Icon"]["SubKind"] if i["Icon"]["SubKind"] != "投掷囊" else "暗器"
            attrs_data = i["ModifyType"]
            attrs_list = []
            for x in attrs_data:
                string = x["Attrib"]["GeneratedMagic"]
                flag = False
                for y in filter_words:
                    if string.find(y) != -1:
                        flag = True
                if flag:
                    continue
                attrs_list.append(string)
            attrs = "<br>".join(attrs_list)
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
            tablecontent.append(template_drop.replace("$icon", icon).replace("$name", name).replace("$attrs", attrs).replace(
                "$type", type_).replace("$stars", stars).replace("$quailty", quailty).replace("$score", score).replace("$fivestone", fivestone))
        for i in others:
            type_ = "不适用"
            icon = i["Icon"]["FileName"]
            name = i["Name"]
            attrs = "不适用"
            stars = "不适用"
            score = "不适用"
            quailty = "不适用"
            fivestone = "不适用"
            tablecontent.append(template_drop.replace("$icon", icon).replace("$name", name).replace("$attrs", attrs).replace(
                "$type", type_).replace("$stars", stars).replace("$quailty", quailty).replace("$score", score).replace("$fivestone", fivestone))
        final_table = "\n".join(tablecontent)
        html = read(VIEWS + "/jx3/drop/drop.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        
        html = html.replace("$font", font).replace("$tablecontent", final_table).replace(
            "$randomsaohua", saohua).replace("$appinfo", f" · 掉落列表 · {mode}{zone} · {boss}")
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        return Path(final_path).as_uri()

template = """
<tr>
    <td class="short-column">$zonename</td>
    <td class="short-column">$zonemode</td>
    <td>
    $images
    </td>
</tr>
"""

unable_ = """
<img src="$imagepath", height="20",width="20"></img>
"""

available_ = """
<img src="$imagepath", height="20",width="20"></img>
"""


async def zone_v2(server, id):
    server = server_mapping(server)
    data = await get_player_local_data(role_name=id, server_name=server)
    details_data = data.format_jx3api()
    if details_data["code"] != 200:
        guid = ""
        return ["唔……获取玩家信息失败。"]
    else:
        guid = details_data["data"]["globalRoleId"]
    ts = gen_ts()
    param = {
        "globalRoleId": guid,
        "sign": dungeon_sign(f"globalRoleId={guid}&ts={ts}"),
        "ts": ts
    }
    param = format_body(param)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "m.pvp.xoyo.com",
        "Origin": "https://w.pvp.xoyo.com:31727",
        "User-Agent": "SeasunGame/178 CFNetwork/1240.0.2 Darwin/20.5.0",
        "token": ticket,
        "X-Sk": gen_xsk(param)
    }
    data = await post_url("https://m.pvp.xoyo.com/h5/parser/cd-process/get-by-role", headers=headers, data=param)
    unable = unable_.replace("$imagepath", ASSETS + "/image/grey.png")
    available = available_.replace("$imagepath", ASSETS + "/image/gold.png")
    data = json.loads(data)
    if data["data"] == []:
        return ["该玩家目前尚未打过任何副本哦~\n注意：10人普通副本会在周五刷新一次。"]
    else:
        contents = []
        if type(data) == type(None):
            return ["获取玩家信息失败！"]
        for i in data["data"]:
            images = []
            map_name = i["mapName"]
            map_type = i["mapType"]
            for x in i["bossProgress"]:
                if x["finished"] is True:
                    images.append(unable)
                else:
                    images.append(available)
            image_content = "\n".join(images)
            temp = template.replace("$zonename", map_name).replace(
                "$zonemode", map_type).replace("$images", image_content)
            contents.append(temp)
        content = "\n".join(contents)
        html = read(VIEWS + "/jx3/teamcd/teamcd.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        
        html = html.replace("$customfont", font).replace("$tablecontent", content).replace("$randomsaohua", saohua).replace("$appinfo", f" · 副本记录 · {server} · {id}")
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        return Path(final_path).as_uri()

template_item = """
<tr>
    <td class="short-column">$server</td>
    <td class="short-column">$name</td>
    <td class="short-column">$map</td>
    <td class="short-column">$id</td>
    <td class="short-column">$time</td>
    <td class="short-column">$relate</td>
</tr>
"""


async def get_item_record(name: str):
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Microsoft Edge\";v=\"114\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Referer": "https://www.jx3mm.com/jx3fun/jevent/jcitem.html"
    }
    filter = {
        "Zone": "",
        "Srv": "",
        "Droppedi": name
    }
    base_params = {
        "sort": "Tm",
        "order": "desc",
        "limit": 30,
        "offset": 0,
        "_": int(time.time()) * 1000,
        "filter": json.dumps(filter, ensure_ascii=False),
        "op": "{\"Zone\":\"LIKE\",\"Srv\":\"LIKE\"}"
    }
    data = await get_api(url="https://www.jx3mm.com/jx3fun/jevent/jcitem", headers=headers, params=base_params)
    if data["total"] == 0:
        return ["未找到相关物品，请检查物品名称是否正确！"]
    known_time = []
    known_id = []
    tablecontents = []
    font = ASSETS + "/font/custom.ttf"
    num = 0
    for i in data["rows"]:
        if i["Tm"] in known_time and i["Nike"] in known_id:
            continue
        known_time.append(i["Tm"])
        known_id.append(i["Nike"])
        id = i["Nike"]
        item_name = i["Droppedi"]
        if i["Copyname"][0:2] in ["英雄", "普通"]:
            zone = "25人" + i["Copyname"]
        else:
            zone = i["Copyname"]
        timeGet = convert_time(i["Tm"])
        relateTime = getRelateTime(getCurrentTime(), i["Tm"])
        server = i["Srv"]
        tablecontents.append(template_item.replace("$server", server).replace("$name", item_name).replace(
            "$map", zone).replace("$id", id).replace("$time", timeGet).replace("$relate", relateTime))
        num += 1
        if num == 30:
            break  # 不限？不限给你鲨了
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    appinfo_time = convert_time(getCurrentTime(), "%H:%M:%S")
    appinfo = f"掉落统计 · {server} · {name} · {appinfo_time}"
    final_table = "\n".join(tablecontents)
    html = read(VIEWS + "/jx3/item/item.html")
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", appinfo)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()
