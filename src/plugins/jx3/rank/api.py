from src.tools.dep.api import *
from src.tools.dep.server import *
from src.tools.utils import post_url
from src.tools.config import Config
from src.plugins.help import css
from src.tools.generate import generate, get_uuid

from tabulate import tabulate

from .top100 import *
from . import CACHE

import datetime
import hashlib
import hmac

jx3_token = Config.jx3_token

async def rank_(type_1: str, type_2: str, server: str, group_id: str):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    if token == None:
        return [PROMPT_NoToken]
    final_url = f"https://www.jx3api.com/view/rank/excellent?token={token}&robot={bot}&server={server}&table={type_1}&name={type_2}&scale=1"
    if type_1 == "个人":
        if type_2 not in ["名士五十强", "老江湖五十强", "兵甲藏家五十强", "名师五十强", "阵营英雄五十强", "薪火相传五十强", "庐园广记一百强"]:
            return ["唔……类型不正确，请检查后重试~"]
    elif type_1 == "帮会":
        if type_2 not in ["浩气神兵宝甲五十强", "恶人神兵宝甲五十强", "浩气爱心帮会五十强", "恶人爱心帮会五十强"]:
            return ["唔……类型不正确，请检查后重试~"]
    elif type_1 == "战功":
        if type_2 not in ["赛季恶人五十强", "赛季浩气五十强", "上周恶人五十强", "上周浩气五十强", "本周恶人五十强", "本周浩气五十强"]:
            return ["唔……类型不正确，请检查后重试~"]
    elif type_1 == "试炼":
        if type_2 not in ["万花", "七秀", "少林", "纯阳", "天策", "五毒", "唐门", "明教", "苍云", "长歌", "藏剑", "丐帮", "霸刀", "蓬莱", "凌雪", "衍天", "药宗", "刀宗"]:
            return ["唔……门派不正确哦，请检查后重试~"]
    else:
        return ["未知类型，只能是个人/帮会/战功/试炼哦！"]
    data = await get_api(final_url, proxy=proxies)
    if data["code"] == 400:
        return [PROMPT_ArgumentInvalid]
    if data["code"] == 404:
        return ["唔……未收录！"]
    return data["data"]["url"]

def format_body(data: dict) -> str:
    return json.dumps(data, separators=(',', ':'))

def gen_ts() -> str:
    return f"{datetime.datetime.now():%Y%m%d%H%M%S%f}"[:-3]

def gen_xsk(data: str) -> str:
    data += "@#?.#@"
    secret = "MaYoaMQ3zpWJFWtN9mqJqKpHrkdFwLd9DDlFWk2NnVR1mChVRI6THVe6KsCnhpoR"
    return hmac.new(secret.encode(), msg=data.encode(), digestmod=hashlib.sha256).hexdigest()

async def zlrank(server: str = None, school: str = None, group_id: str = None):
    school_data = await get_api("https://inkar-suki.codethink.cn/jx3boxdata")
    if school != None:
        flag = False
        for i in school_data:
            if school_data[i] == school:
                school_id = i
                flag = True
        if flag == False:
            return ["未找到该门派哦，请检查后重试~"]
    else:
        school_id = "-1"
    if server == None:
        server = ""
    else:
        server = server_mapping(server, group_id)
        if not server:
            return [PROMPT_ServerNotExist]
    param = {
        "pageId":"5f3a6654de993800113bd1cc",
        "cursor":0,
        "size":50,
        "ts":gen_ts(),
        "serverName": server,
        "forceId": int(school_id)
        }
    param = format_body(param)
    device_id = token.split("::")[1]
    xsk = gen_xsk(param)
    headers = {
            "Host": "m.pvp.xoyo.com",
            "accept": "application/json",
            "deviceid": device_id,
            "platform": "android",
            "gamename": "jx3",
            "fromsys": "APP",
            "clientkey": "1",
            "cache-control": "no-cache",
            "apiversion": "3",
            "sign": "true",
            "token": token,
            "content-type": "application/json",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/3.12.2",
            "x-sk": xsk
    }
    data = await post_url(url="https://m.pvp.xoyo.com/user/list-jx3-topn-roles-info", data=param, headers=headers)
    lank = data["data"]["roles"]
    chart = []
    chart.append(["排行","推栏头像","门派","推栏昵称","游戏角色","资历","区服"])
    num = 1
    for i in lank:
        num = 1
        tuilan_avatar = "<img src=\"" + i["avatarUrl"] + "\", height=\"50\", width=\"50\"></img>"
        school_name = school_data[i["forceId"]]
        nickname = i["nickName"]
        roleName = i["roleName"]
        value = str(i["Value"])
        server_name = i["serverName"]
        new = [str(num), tuilan_avatar, school_name, nickname, roleName, value, server_name]
        chart.append(new)
        num = num + 1
    final_html = css + tabulate(chart, tablefmt="unsafehtml")
    final_path = CACHE + "/" + get_uuid() + ".html"
    write(final_path, final_html)
    img = await generate(final_path, False, "table", False)
    if img == False:
        return ["唔……图片生成失败，请联系机器人管理员解决此问题！"]
    else:
        return img
    