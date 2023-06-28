from src.tools.dep import *
from src.tools.generate import generate, get_uuid
from src.plugins.help import css

from tabulate import tabulate

import hmac
import hashlib

async def zone(server, id):
    server = server_mapping(server)
    final_url = f"https://www.jx3api.com/view/role/teamCdList?token={token}&server={server}&name={id}&ticket={ticket}&robot={bot}&scale=1"
    data = await get_api(final_url)
    if data["code"] == 404:
        return ["玩家不存在或尚未在世界频道发言哦~"]
    return data["data"]["url"]

async def get_cd(server: str, sep: str):
    url = f"https://pull.j3cx.com/api/serendipity?server={server}&serendipity={sep}&pageSize=1"
    data = await get_api(url)
    data = data.get("data").get('data')
    if not data:
        return "没有记录哦~"
    data = data[0]
    time = data["date_str"]
    msg = f"「{server}」服务器上一次记录「{sep}」：\n{time}\n数据来源：@茗伊插件集"
    return msg

def format_body(data: dict) -> str:
    return json.dumps(data, separators=(',', ':'))

def gen_ts() -> str:
    return f"{datetime.datetime.now():%Y%m%d%H%M%S%f}"[:-3]

def gen_xsk(data: str) -> str:
    data += "@#?.#@"
    secret = "MaYoaMQ3zpWJFWtN9mqJqKpHrkdFwLd9DDlFWk2NnVR1mChVRI6THVe6KsCnhpoR"
    return hmac.new(secret.encode(), msg=data.encode(), digestmod=hashlib.sha256).hexdigest()

async def post_url(url, proxy: dict = None, headers: str = None, timeout: int = 300, data: dict = None):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects = True) as client:
        resp = await client.post(url, timeout = timeout, headers = headers, data = data)
        result = resp.text
        return result

async def get_map(name, mode):
    param = {
        "mode": 2,
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
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
            "x-sk": xsk
    }
    data = await post_url(url="https://m.pvp.xoyo.com/dungeon/boss-drop", data=param, headers=headers)
    return json.loads(data)

def mode_mapping(mode):
    if mode in ["25yx","yx","YX","Yx","yX","25人YX","25人英雄","英雄","25Yx","25人yX","25人yx","25英雄"]:
        return "25人英雄"
    elif mode in ["25pt","PT","pt","pT","25人PT","25人Pt","25人pt","25普通","普通","25人普通","25pt","铂"]:
        return "25人普通"
    elif mode in ["10人","10","10人普通","10PT","10pt"]:
        return "10人普通"
    elif mode in ["10人yx","10人英雄","10YX","10yx"]:
        return "10人英雄"
    elif mode in ["10人tz","10tz","10TZ","10Tz","10人挑战","10挑战"]:
        return "10人挑战"
    elif mode in ["25人tz","tz","TZ","Tz","25挑战","25人挑战","25TZ","25tz"]:
        return "25人挑战"
    else:
        return False

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
    chart = [["装备"]]
    if armors == None:
        chart.append(["无"])
    new = []
    num = 0
    for i in armors:
        ado = []
        ads = []
        flag = False
        try:
            adtb = i["ModifyType"]
            flag = True
        except:
            flag = False
        if flag:
            for x in adtb:
                ctt = x["Attrib"]["GeneratedMagic"]
                if ctt.find("提高") != -1:
                    adc = ctt.split("提高")[0]
                else:
                    adc = ctt.split("增加")[0]
                ado.append(adc)
            for x in ado:
                for y in ["阴性","阳性","全","阴阳","体质","等级","混元性","攻击","成效","值","毒性","御","招式产生威胁","功"]:
                    x = x.replace(y, "")
                ads.append(x)
            while True:
                try:
                    ads.remove("")
                except ValueError:
                    break
        else:
            pass
        if i["Icon"]["SubKind"] in ["腰部挂件","背部挂件","披风"]:
            name = "<span style=\"text-align: center;\">" + i["Name"] + "<br>（" + i["Icon"]["SubKind"] + "）" + "</span>"
        else:
            name = "<span style=\"text-align: center;\">" + i["Name"] + "<br>（" + i["MaxStrengthLevel"] + "·" + i["Quality"] +"）" + "</span>"
        icon = "<img src=\"" + i["Icon"]["FileName"] + "\"></img>"
        final = icon + "<br>" + name
        if flag:
            final = final + "<br>" + "|".join(ads)
        new.append(final)
        num = num + 1
        if num == 8:
            chart.append(new)
            new = []
            num = 0
    num = 0
    if len(new) != 0:
        chart.append(new)
    new = []
    chart.append(["武器"])
    for i in weapons:
        ado = []
        ads = []
        adtb = i["ModifyType"]
        for x in adtb:
            ctt = x["Attrib"]["GeneratedMagic"]
            if ctt.find("提高") != -1:
                adc = ctt.split("提高")[0]
            else:
                adc = ctt.split("增加")[0]
            ado.append(adc)
        for x in ado:
            for y in ["阴性","阳性","全","阴阳","体质","等级","混元性","攻击","成效","值","毒性","御","招式产生威胁","功"]:
                x = x.replace(y, "")
            ads.append(x)
        while True:
            try:
                ads.remove("")
            except ValueError:
                break
        ad = "|".join(ads)
        name = "<span style=\"text-align: center;\">" + i["Name"] + "<br>（" + i["MaxStrengthLevel"] + "·" + i["Quality"] + "）" + "</span>"
        force = i["BelongForce"]
        icon = "<img src=\"" + i["Icon"]["FileName"] + "\"></img>"
        final = icon + "<br>" + name + "<br>" + force + "<br>" + ad
        new.append(final)
        num = num + 1
        if num == 8:
            chart.append(new)
            new = []
            num = 0
    num = 0
    if len(new) != 0:
        chart.append(new)
    new = []
    chart.append(["其他"])
    for i in others:
        name = "<span style=\"text-align: center;\">" + i["Name"] + "</span>"
        icon = "<img src=\"" + i["Icon"]["FileName"] + "\"></img>"
        final = icon + "<br>" + name
        new.append(final)
        num = num + 1
        if num == 8:
            chart.append(new)
            new = []
            num = 0
    num = 0
    if len(new) != 0:
        chart.append(new)
    html = css + tabulate(chart, tablefmt="unsafehtml")
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, html)
    img = await generate(final_path, False, "table", False)
    if img == False:
        return ["唔……生成失败，请联系音卡管理员！"]
    return img