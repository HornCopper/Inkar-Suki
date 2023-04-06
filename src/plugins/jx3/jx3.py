import nonebot
import sys
import json

from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.log import logger

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
DATA = TOOLS[:-5] + "data"

from utils import get_api, nodetemp
from file import write, read
from .skilldatalib import aliases
from config import Config

token = Config.jx3api_globaltoken
bot = "Inkar-Suki"
ticket = Config.jx3_token

proxy = Config.proxy

if proxy != None:
    proxies = {
    "http://": proxy,
    "https://": proxy
    }
else:
    proxies = None

'''
根据`__init__.py`的各功能而设计的功能函数。

数据来源@JX3API
'''

async def server_status(server: str = None, group: str = None):
    server = server_mapping(server, group)
    if server == False:
        return ["唔……服务器名输入错误。"]
    full_link = "https://www.jx3api.com/data/server/check?server=" + server
    info = await get_api(full_link, proxy = proxies)
    try:
        all_servers = info["data"]
        if str(type(all_servers)).find("list") != -1:
            return "服务器名输入错误。"
    except:
        pass
    status = info["data"]["status"]
    if status == 1:
        return f"{server}服务器并未维护。"
    elif status == 0:
        return f"{server}服务器维护中。"

async def daily_(server: str = None, group: str = None):
    server = server_mapping(server, group_id = group)
    if server == False:
        return ["唔……服务器名输入错误。"]
    full_link = f"https://www.jx3api.com/view/active/current?robot={bot}&server={server}"
    data = await get_api(full_link, proxy = proxies)
    return data["data"]["url"]

async def exam_(question):
    def qa(q, a):
        return f"问题：{q}\n答案：{a}"
    full_link = "https://www.jx3api.com/data/exam/answer?match=" + question
    info = await get_api(full_link, proxy = proxies)
    if info["code"] == 400:
        return "没有找到任何与此相关的题目哦~"
    else:
        msg = ""
    msg = "找到下列相似的题目：\n"
    for i in info["data"]:
        msg = msg + qa(i["question"],i["answer"]) + "\n"
    return msg
    
async def matrix_(name):
    name = aliases(name)
    if name == False:
        return "此心法不存在哦~请检查后重试。"
    full_link = "https://www.jx3api.com/data/school/matrix?name=" + name
    info = await get_api(full_link, proxy = proxies)
    if info["code"] == 400:
        return "此心法不存在哦~请检查后重试。"
    else:
        description = ""
        def fe(f, e):
            return f"{f}：{e}\n"
        for i in info["data"]["descs"]:
            description = description + fe(i["name"], i["desc"])
        skillName = info["data"]["skillName"]
        return f"查到了{name}的{skillName}：\n" + description
        
async def news_():
    full_link = "https://api.jx3api.com/data/web/news?limit=5"
    info = await get_api(full_link, proxy = proxies)
    def dtut(date, title, url, type_):
        return f"{date}{type_}：{title}\n{url}"
    msg = ""
    for i in info["data"]:
        msg = msg + dtut(i["date"], i["title"], i["url"], i["type"]) + "\n"
    return msg

async def random__():
    full_link = "https://www.jx3api.com/data/saohua/random"
    info = await get_api(full_link, proxy = proxies)
    return info["data"]["text"]

async def tiangou_():
    full_link = "https://www.jx3api.com/data/saohua/content"
    data = await get_api(full_link, proxy = proxies)
    text = data["data"]["text"]
    return text

async def recruit_(server: str, copy: str = "", group: str = None): # 团队招募 <服务器> [关键词]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server, group)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/member/recruit?token={token}&server={server}&robot={bot}&scale=1&keyword="
    if copy != None:
        final_url = final_url + copy
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 403:
        return ["Token不正确哦，请联系Bot主人~"]
    elif data["code"] == 400:
        return ["服务器名输入错误，请检查后重试~"]
    elif data["code"] == 404:
        return ["未找到相关团队，请检查后重试~"]
    url = data["data"]["url"]
    return url

async def demon_(server: str = None, group: str = None): # 金价 <服务器>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if server == None:
        return ["服务器名输入错误，请检查后重试~"]
    else:
        server = server_mapping(server, group)
        if server == False:
            return ["唔……服务器名输入错误。"]
        final_url = f"https://www.jx3api.com/view/trade/demon?robot={bot}&server={server}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 400:
        return ["服务器名输入错误，请检查后重试~"]
    return data["data"]["url"]

async def item_(name: str = None): # 物价 <物品>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    final_url = f"https://www.jx3api.com/view/trade/record?token={token}&robot={bot}&name={name}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return ["唔……尚未收录该物品。"]
    return data["data"]["url"]

async def serendipity_(server: str = None, name: str = None, group: str = None): # 奇遇 <服务器> <ID>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server, group)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/luck/adventure?token={token}&robot={bot}&ticket={ticket}&server={server}&name={name}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def statistical_(server: str = None, serendipity: str = None, group: str = None): # 近期奇遇 <服务器> [奇遇]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server, group)
    if server == False:
        return ["唔……服务器名输入错误。"]
    if serendipity == None:
        final_url = f"https://www.jx3api.com/view/luck/collect?token={token}&robot={bot}&server={server}&scale=1"
    else:
        final_url = f"https://www.jx3api.com/view/luck/statistical?token={token}&robot={bot}&ticket={ticket}&server={server}&name={serendipity}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def global_serendipity(name: str = None): # 全服奇遇 [奇遇]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if name != None:
        final_url = f"https://www.jx3api.com/view/luck/server/adventure?name={name}&token={token}&robot={bot}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def global_statistical(name: str = None): # 全服统计 [奇遇]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if name != None:
        final_url = f"https://www.jx3api.com/view/luck/server/statistical?name={name}&token={token}&robot={bot}"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def addritube_(server: str = None, name: str = None, group: str = None): # 查装 <服务器> <ID>
    if token == None or ticket == None:
        return ["Bot尚未填写Ticket或Token，请联系Bot主人~"]
    server = server_mapping(server, group)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/role/attribute?ticket={ticket}&token={token}&robot={bot}&server={server}&name={name}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return ["唔……玩家不存在。"]
    if data["code"] == 403 and data["msg"] == "侠客隐藏了游戏信息":
        return ["唔，该玩家隐藏了信息。"]
    if data["code"] == 403 and data["msg"] == "仅互关好友可见":
        return ["仅互关好友可见哦~"]
    return data["data"]["url"]

async def sandbox_(server: str = None, group: str = None): # 沙盘 <服务器>
    server = server_mapping(server, group)
    if server == False:
        return ["唔……服务器名输入错误。"]
    if server != None:
        final_url = f"https://www.jx3api.com/view/server/sand?token={token}&scale=1&robot={bot}&server=" + server
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 400:
        return ["唔……服务器名输入错误。"]
    return data["data"]["url"]

async def achievements_(server: str = None, name: str = None, achievement: str = None, group: str = None):
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if ticket == None:
        return ["Bot尚未填写Ticket，请联系Bot主人~"]
    server = server_mapping(server, group_id = group)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/role/achievement?server={server}&name={achievement}&role={name}&robot={bot}&ticket={ticket}&token={token}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 400:
        return ["唔……服务器名输入错误。"]
    if data["data"] == {}:
        return ["唔……未找到相应成就。"]
    if data["code"] == 404:
        return ["唔……玩家名输入错误。"]
    return data["data"]["url"]

async def arena_(object: str, server: str = None, name: str = None, mode: str = "33", group: str = None):
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if ticket == None:
        return ["Bot尚未填写Ticket，请联系Bot主人~"]
    if object == "战绩":
        server = server_mapping(server, group)
        if server == False:
            return ["唔……服务器名输入错误。"]
        final_url = f"https://www.jx3api.com/view/match/recent?token={token}&name={name}&server={server}&robot={bot}&ticket={ticket}&mode={mode}&scale=1"
        data = await get_api(final_url, proxy = proxies)
        if data["code"] == 400:
            return ["唔……服务器名输入错误。"]
        if data["code"] == 404:
            return ["唔……未找到该玩家的记录，请检查玩家名或服务器名。"]
        return data["data"]["url"]
    elif object == "排行":
        final_url = f"https://www.jx3api.com/view/match/awesome?token={token}&robot={bot}&ticket={ticket}&mode={mode}&scale=1"
        data = await get_api(final_url, proxy = proxies)
        if data["code"] == 400:
            return ["唔……名剑模式输入错误。"]
        return data["data"]["url"]
    elif object == "统计":
        final_url = f"https://www.jx3api.com/data/match/schools?token={token}&robot={bot}&ticket={ticket}&mode={mode}&scale=1"
        data = await get_api(final_url, proxy = proxies)
        if data["code"] == 400:
            return ["唔……名剑模式输入错误。"]
        return data["data"]["url"]

async def rank_(type_1: str, type_2: str, server: str, group: str = None):
    server = server_mapping(server, group)
    if server == False:
        return ["唔……服务器名输入错误。"]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if type_1 == "个人":
        if type_2 not in ["名士五十强","老江湖五十强","兵甲藏家五十强","名师五十强","阵营英雄五十强","薪火相传五十强","庐园广记一百强"]:
            return ["唔……类型不正确，请检查后重试~"]
        final_url = f"https://api.jx3api.com/view/rank/various?token={token}&robot={bot}&server={server}&type={type_2}"
    elif type_1 == "帮会":
        if type_2 not in ["浩气神兵宝甲五十强","恶人神兵宝甲五十强","浩气爱心帮会五十强","恶人爱心帮会五十强"]:
            return ["唔……类型不正确，请检查后重试~"]
        final_url = f"https://api.jx3api.com/view/rank/tribe?token={token}&robot={bot}&server={server}&type={type_2}"
    elif type_1 == "战功":
        if type_2 not in ["赛季恶人五十强","赛季浩气五十强","上周恶人五十强","上周浩气五十强","本周恶人五十强","本周浩气五十强"]:
            return ["唔……类型不正确，请检查后重试~"]
        final_url = f"https://api.jx3api.com/view/rank/excellent?token={token}&robot={bot}&server={server}&type={type_2}"
    elif type_1 == "试炼":
        if type_2 not in ["万花","七秀","少林","纯阳","天策","五毒","唐门","明教","苍云","长歌","藏剑","丐帮","霸刀","蓬莱","凌雪","衍天","药宗","刀宗"]:
            return ["唔……门派不正确哦，请检查后重试~"]
        final_url = f"https://www.jx3api.com/data/rank/excellent?token={token}&robot={bot}&server={server}&type={type_2}&scale=1"
    else:
        return ["未知类型，只能是个人/帮会/战功/试炼哦！"]
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 400:
        return ["唔……参数有误！"]
    if data["code"] == 404:
        return ["唔……未收录！"]
    return data["data"]["url"]

async def announce_():
    final_url = f"https://www.jx3api.com/view/web/announce?robot={bot}"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def roleInfo_(server, player, group: str = None):
    server = server_mapping(server, group)
    final_url = f"https://www.jx3api.com/data/role/roleInfo?token={token}&name={player}&server={server}"
    if server == False:
        return "唔……服务器名输入错误。"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return "没有找到该玩家哦~\n需要该玩家在世界频道发言后方可查询。"
    msg = "以下信息仅供参考！\n数据可能已经过期，但UID之类的仍可参考。"
    zone = data["data"]["zoneName"]
    srv = data["data"]["serverName"]
    nm = data["data"]["roleName"]
    uid = data["data"]["roleId"]
    fc = data["data"]["forceName"]
    bd = data["data"]["bodyName"]
    tg = data["data"]["tongName"]
    cp = data["data"]["campName"]
    msg = msg + f"\n服务器：{zone} - {srv}\n角色名称：{nm}\nUID：{uid}\n体型：{fc}·{bd}\n帮会：{cp} - {tg}"
    return msg
    
async def zone(server, id, group):
    server = server_mapping(server, group)
    final_url = f"https://www.jx3api.com/view/role/teamCdList?token={token}&server={server}&name={id}&ticket={ticket}&robot={bot}&scale=1"
    data = await get_api(final_url)
    if data["code"] == 404:
        return ["玩家不存在或尚未在世界频道发言哦~"]
    return data["data"]["url"]

def server_mapping(server: str, group_id: str):
    if server in ["二合一","四合一","六合一","七合一","千岛湖","圣墓山","执子之手","平步青云","笑傲江湖","幽月轮","山雨欲来"]:
        return "幽月轮"
    elif server in ["剑胆琴心","煎蛋","剑胆"]:
        return "剑胆琴心"
    elif server in ["梦江南","双梦","如梦令","枫泾古镇","双梦镇"]:
        return "梦江南"
    elif server in ["斗转星移","金戈铁马","风雨同舟","大唐万象","姨妈","风雨","风雨大姨妈"]:
        return "斗转星移"
    elif server in ["长安城"]:
        return "长安城"
    elif server in ["电八","电信八区","绝代天骄","风骨霸刀","绝代双骄"]:
        return "绝代天骄"
    elif server in ["龙虎","龙争虎斗"]:
        return "龙争虎斗"
    elif server in ["唯满侠","唯我独尊"]:
        return "唯我独尊"
    elif server in ["华山论剑","乾坤一掷","花钱","华乾"]:
        return "乾坤一掷"
    elif server in ["蝶服","蝶恋花"]:
        return "蝶恋花"
    elif server in ["纵月","天鹅坪"]:
        return "天鹅坪"
    elif server in ["青梅煮酒","青梅"]:
        return "青梅煮酒"
    elif server in ["横刀断浪","横刀"]:
        return "横刀断浪"
    elif server in ["破阵子","念破"]:
        return "破阵子"
    elif server in ["飞龙在天","飞龙"]:
        return "飞龙在天"
    else:
        binded = getGroupServer(group_id)
        if binded == False:
            return False
        else:
            return binded
        
# 服务器绑定群聊的意义在此体现。
    
def getGroupServer(group):
    data = json.loads(read(DATA + "/" + group + "/jx3group.json"))
    if data["name"] == "":
        return False
    else:
        return data["server"]