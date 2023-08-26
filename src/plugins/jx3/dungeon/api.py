import re

from tabulate import tabulate

from src.tools.dep import *
from src.tools.generate import generate, get_uuid
from src.plugins.help import css

ASSETS = TOOLS[:-5] + "assets"
VIEWS = TOOLS[:-5] + "views"

try:
    from src.tools.dep.jx3.tuilan import gen_ts, gen_xsk, format_body, dungeon_sign # 收到热心网友举报，我们已对推栏的算法进行了隐藏。
except:
    pass

async def zone(server, id):
    server = server_mapping(server)
    final_url = f"{Config.jx3api_link}/view/role/teamCdList?token={token}&server={server}&name={id}&ticket={ticket}&robot={bot}&scale=1"
    data = await get_api(final_url)
    if data["code"] == 404:
        return ["玩家不存在或尚未在世界频道发言哦~"]
    return data["data"]["url"]

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

async def post_url(url, proxy: dict = None, headers: str = None, timeout: int = 300, data: dict = None):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects=True) as client:
        resp = await client.post(url, timeout=timeout, headers=headers, data=data)
        result = resp.text
        return result

device_id = ticket.split("::")[1]

async def get_map(name, mode):
    param = {
        "mode": 2,
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host" : "m.pvp.xoyo.com",
        "Accept" : "application/json",
        "Accept-Language" : "zh-cn",
        "Connection" : "keep-alive",
        "Content-Type" : "application/json",
        "cache-control" : "no-cache",
        "fromsys" : "APP",
        "clientkey" : "1",
        "apiversion" : "3",
        "gamename" : "jx3",
        "platform" : "ios",
        "sign" : "true",
        "token" : ticket,
        "deviceid" : device_id,
        "User-Agent" : "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
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
        "Host" : "m.pvp.xoyo.com",
        "Accept" : "application/json",
        "Accept-Language" : "zh-cn",
        "Connection" : "keep-alive",
        "Content-Type" : "application/json",
        "cache-control" : "no-cache",
        "fromsys" : "APP",
        "clientkey" : "1",
        "apiversion" : "3",
        "gamename" : "jx3",
        "platform" : "ios",
        "sign" : "true",
        "token" : ticket,
        "deviceid" : device_id,
        "User-Agent" : "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
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
        "Host" : "m.pvp.xoyo.com",
        "Accept" : "application/json",
        "Accept-Language" : "zh-cn",
        "Connection" : "keep-alive",
        "Content-Type" : "application/json",
        "cache-control" : "no-cache",
        "fromsys" : "APP",
        "clientkey" : "1",
        "apiversion" : "3",
        "gamename" : "jx3",
        "platform" : "ios",
        "sign" : "true",
        "token" : ticket,
        "deviceid" : device_id,
        "User-Agent" : "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
        "x-sk": xsk
    }
    data = await post_url(url="https://m.pvp.xoyo.com/dungeon/boss-drop", data=param, headers=headers)
    return json.loads(data)


def mode_mapping(mode):
    if mode in ["25yx", "yx", "YX", "Yx", "yX", "25人YX", "25人英雄", "英雄", "25Yx", "25人yX", "25人yx", "25英雄"]:
        return "25人英雄"
    elif mode in ["25pt", "PT", "pt", "pT", "25人PT", "25人Pt", "25人pt", "25普通", "普通", "25人普通", "25pt", "铂"]:
        return "25人普通"
    elif mode in ["10人", "10", "10人普通", "10PT", "10pt"]:
        return "10人普通"
    elif mode in ["10人yx", "10人英雄", "10YX", "10yx"]:
        return "10人英雄"
    elif mode in ["10人tz", "10tz", "10TZ", "10Tz", "10人挑战", "10挑战"]:
        return "10人挑战"
    elif mode in ["25人tz", "tz", "TZ", "Tz", "25挑战", "25人挑战", "25TZ", "25tz"]:
        return "25人挑战"
    else:
        return False

star = """
<svg width="20" height="20">
    <polygon points="10,0 13,7 20,7 14,12 16,19 10,15 4,19 6,12 0,7 7,7" style="fill:gold; stroke:gold; stroke-width:1px;" />
</svg>
"""

template = """
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

equip_types = ["帽子","上衣","腰带","护臂","裤子","鞋","项链","腰坠","戒指","投掷囊"]

filter_words = ["根骨","力道","元气","身法","体质"]

async def genderater(map, mode, boss):
    mode = mode_mapping(mode)
    if mode == False:
        return ["唔……难度似乎音卡不能理解哦~"]
    try:
        data = await get_drops(map, mode, boss)
    except KeyError:
        return ["唔……没有找到该掉落列表，请检查副本名称、BOSS名称或难度~"]
    data = data["data"]
    armors = data["armors"]
    others = data["others"]
    weapons = data["weapons"]
    if len(armors) == 0 and len(others) == 0 and len(weapons) == 0:
        return ["唔……没有找到该boss的掉落哦~\n您确定" + f"{boss}住在{mode}{map}吗？"]
    else:
        tablecontent = []
        for i in armors:
            name = i["Name"]
            icon = i["Icon"]["FileName"]
            if i["Icon"]["SubKind"] in equip_types and i["Type"] != "Act_运营及版本道具":
                type_ = "装备"
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
                if i["type"] != "戒指":
                    diamon_data = i["DiamonAttribute"]
                    diamon_list = []
                    for x in diamon_data:
                        string = re.sub(r"\b+", "", x["Attrib"]["GeneratedMagic"]) + "?"
                        diamon_list.append(string)
                    fivestone = "<br>".join(diamon_list)
                else:
                    fivestone = "不适用"
                max = i["MaxStrengthLevel"]
                stars = []
                for x in range(int(max)):
                    stars.append(star)
                stars = "\n".join(stars)
                quailty = i["Quality"]
                equip_type = i["Icon"]["SubKind"]
                if equip_type == "帽子":
                    score = str(int(quailty)*1.62)
                elif equip_type in ["上衣","裤子"]:
                    score = str(int(quailty)*1.8)
                elif equip_type in ["腰带","护臂","鞋"]:
                    score = str(int(quailty)*1.26)
                elif equip_type in ["项链","腰坠","戒指"]:
                    score = str(int(quailty)*0.9)
                elif equip_type in ["投掷囊"]:
                    score = str(int(quailty)*1.08)
            else:
                if i["Type"] == "Act_运营及版本道具":
                    type_ = "外观"
                else:
                    type_ = re.sub(r"\d+", "", i["Icon"]["SubKind"])
                attrs = "不适用"
                fivestone = "不适用"
                max = "不适用"
                quailty = "不适用"
                score = "不适用"
            tablecontent.append(template.replace("$icon", icon).replace("$name", name).replace("$attrs", attrs).replace("$type", type_).replace("$stars", stars).replace("$quailty", quailty).replace("$score", score).replace("$fivestone", fivestone))
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
                string = re.sub(r"\b+", "", x["Attrib"]["GeneratedMagic"]) + "?"
                diamon_list.append(string)
            fivestone = "<br>".join(diamon_list)
            max = i["MaxStrengthLevel"]
            stars = []
            for x in range(int(max)):
                stars.append(star)
            stars = "\n".join(stars)
            quailty = i["Quality"]
            score = str(int(quailty)*2.16)
            tablecontent.append(template.replace("$icon", icon).replace("$name", name).replace("$attrs", attrs).replace("$type", type_).replace("$stars", stars).replace("$quailty", quailty).replace("$score", score).replace("$fivestone", fivestone))
        for i in others:
            type_ = "不适用"
            icon = i["Icon"]["FileName"]
            name = i["Name"]
            attrs = "不适用"
            stars = "不适用"
            score = "不适用"
            quailty = "不适用"
            fivestone = "不适用"
            tablecontent.append(template.replace("$icon", icon).replace("$name", name).replace("$attrs", attrs).replace("$type", type_).replace("$stars", stars).replace("$quailty", quailty).replace("$score", score).replace("$fivestone", fivestone))
        final_table = "\n".join(tablecontent)
        html = read(VIEWS + "/jx3/drop/drop.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
        saohua = saohua["data"]["text"]
        html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f" · 掉落列表 · {mode}{map} · {boss}")
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
    details_request = f"{Config.jx3api_link}/data/role/detailed?token={token}&server={server}&name={id}"
    details_data = await get_api(details_request)
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
        for i in data["data"]:
            images = []
            map_name = i["mapName"]
            map_type = i["mapType"]
            for x in i["bossProgress"]:
                if x["finished"] == True:
                    images.append(unable)
                else:
                    images.append(available)
            image_content = "\n".join(images)
            temp = template.replace("$zonename", map_name).replace("$zonemode", map_type).replace("$images", image_content)
            contents.append(temp)
        content = "\n".join(contents)
        html = read(VIEWS + "/jx3/teamcd/teamcd.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
        saohua = saohua["data"]["text"]
        html = html.replace("$customfont", font).replace("$tablecontent", content).replace("$randomsaohua", saohua).replace("$appinfo", f" · 副本记录 · {server} · {id}")
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        return Path(final_path).as_uri()