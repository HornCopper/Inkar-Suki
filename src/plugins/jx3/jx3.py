import nonebot
import sys
import json

from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.log import logger

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import get_api, nodetemp
from file import write, read
from .skilldatalib import aliases
from config import Config

proxy = Config.proxy

if proxy != None:
    proxies = {
    "http://": proxy,
    "https://": proxy
    }
else:
    proxies = None

async def server_status(server: str = None):
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    full_link = "https://www.jx3api.com/data/server/check?server="+server
    info = await get_api(full_link, proxy = proxies)
    try:
        all_servers = info["data"]
        if str(type(all_servers)).find("list") != -1:
            return "服务器名输入错误。"
    except:
        pass
    status = info["data"]["status"]
    if status == 1:
        return f"{server}服务器状态正常。"
    elif status == 0:
        return f"{server}服务器维护中。"

async def horse_flush_place(horse_name):
    def template(place, img):
        return f"刷新地点：{place}\n" + ms.image(img)
    full_link = "https://www.jx3api.com/data/useless/refresh?name="+horse_name
    info = await get_api(full_link, proxy = proxies)
    if info["code"] == 401:
        return "未找到对应马匹。"
    msg = ""
    maps = info["data"]["data"]
    if len(maps) <1:
        return "该马匹没有刷新地点。"
    for i in maps:
        msg = msg + template(i["map"],i["url"])
    return msg

async def macro_(name):
    name = aliases(name)
    if name == False:
        return "此心法不存在哦~请检查后重试。"
    full_link = "https://www.jx3api.com/data/school/macro?name=" + name
    info = await get_api(full_link, proxy = proxies)
    if info["code"] == 401:
        return "此心法不存在哦~请检查后重试。"
    qixue = info["data"]["qixue"]
    macro = info["data"]["macro"]
    xinfa = info["data"]["name"]
    return f"查到{xinfa}的宏命令啦！\n推荐奇穴搭配：{qixue}\n宏命令：\n{macro}"
    
async def daily_(server: str = None):
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    full_link = "https://www.jx3api.com/data/active/current?server=" + server
    info = await get_api(full_link, proxy = proxies)
    date = info["data"]["date"]
    week = info["data"]["week"]
    war = info["data"]["war"]
    battle = info["data"]["battle"]
    camp = info["data"]["camp"]
    prestige = info["data"]["prestige"]
    prestige = "，".join(prestige)
    relief = info["data"]["relief"]
    school = info["data"]["school"]
    try:
        draw_obj = info["data"]["draw"]
    except:
        draw_obj = "无（周三、周五、周末才有哦~）"
    weekly_war = info["data"]["team"][1].replace(";","，")
    weekly_big_war = info["data"]["team"][2].replace(";","，")
    weekly_task = info["data"]["team"][0].replace(";","，")
    return f"查到该区服（{date}，周{week}）的信息啦！\n大战：大战！{war}！\n矿车阵营日常：跨服·{camp}\n驰援任务：{relief}\n战场：{battle}\n美人图：{draw_obj}\n世界公共任务：{weekly_task}\n小队秘境周常：{weekly_war}\n团队秘境周常：{weekly_big_war}\n家园声望秘境：{prestige}\n门派事件：{school}"

async def exam_(question):
    def qa(q,a):
        return f"问题：{q}\n答案：{a}"
    full_link = "https://www.jx3api.com/data/exam/search?question="+question
    info = await get_api(full_link, proxy = proxies)
    if info["code"] == 401:
        return "没有找到任何与此相关的题目哦~"
    else:
        msg = ""
    msg = "找到下列相似的题目：\n"
    for i in info["data"]:
        msg = msg + qa(i["question"],i["answer"])+"\n"
    return msg
    
async def matrix_(name):
    name = aliases(name)
    if name == False:
        return "此心法不存在哦~请检查后重试。"
    full_link = "https://www.jx3api.com/data/school/matrix?name="+name
    info = await get_api(full_link, proxy = proxies)
    if info["code"] == 401:
        return "此心法不存在哦~请检查后重试。"
    else:
        description = ""
        def fe(f,e):
            return f"{f}：{e}\n"
        for i in info["data"]["descs"]:
            description = description+fe(i["name"],i["desc"])
        skillName = info["data"]["skillName"]
        return f"查到了{name}的{skillName}：\n" + description
        
async def equip_(name):
    name = aliases(name)
    if name == False:
        return "此心法不存在哦~请检查后重试。"
    full_link = "https://www.jx3api.com/data/school/equip?name="+name
    info = await get_api(full_link, proxy = proxies)
    if info["code"] == 401:
        return "此心法不存在哦~请检查后重试。"
    else:
        return f"找到{name}的推荐装备了：\nPVE：\n"+ms.image(info["data"]["pve"])+"\nPVP：\n"+ms.image(info["data"]["pvp"])
    
async def require_(name):
    full_link = "https://www.jx3api.com/data/lucky/sub/strategy?name="+name
    info = await get_api(full_link, proxy = proxies)
    if info["code"] == 401:
        return "此奇遇不存在或不是绝世/珍稀奇遇哦~请检查后重试。"
    else:
        image = ms.image(info["data"]["url"])
        return image
        
async def news_():
    full_link = "https://www.jx3api.com/data/web/news"
    info = await get_api(full_link, proxy = proxies)
    def dtut(date,title,url,type_):
        return f"{date}{type_}：{title}\n{url}"
    msg = ""
    for i in info["data"]:
        msg = msg + dtut(i["date"],i["title"],i["url"],i["type"]) + "\n"
    return msg

async def random__():
    full_link = "https://www.jx3api.com/data/chat/random"
    info = await get_api(full_link, proxy = proxies)
    return info["data"]["text"]

async def heighten_(name):
    name = aliases(name)
    if name == False:
        return "此心法不存在哦~请检查后重试。"
    full_link = "https://www.jx3api.com/data/school/snacks?name=" + name
    data = await get_api(full_link, proxy = proxies)
    if data["code"] == 401:
        return data["msg"]
    else:
        info = data["data"]
        logger.info(info)
        heighten_food = info["heightenFood"]
        auxiliary_food = info["auxiliaryFood"]
        heighten_drug = info["heightenDrug"]
        auxiliary_drug = info["auxiliaryDrug"]
        return f"查到{name}的推荐小药了：\n增强食品：{heighten_food}\n辅助食品：{auxiliary_food}\n增强药品：{heighten_drug}\n辅助药品：{auxiliary_drug}"

async def tiangou_():
    full_link = "https://www.jx3api.com/data/useless/flatterer"
    data = await get_api(full_link, proxy = proxies)
    text = data["data"]["text"]
    return text

token = Config.jx3api_globaltoken
bot = "Inkar-Suki"
ticket = Config.jx3_token

async def recruit_(server: str, copy: str = None): # 团队招募 <服务器> [关键词]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/team/member/recruit?token={token}&server={server}&robot={bot}&keyword="
    if copy != None:
        final_url = final_url + copy
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 403:
        return ["Token不正确哦，请联系Bot主人~"]
    elif data["code"] == 401:
        return ["服务器名输入错误，请检查后重试~"]
    elif data["code"] == 404:
        return ["未找到相关团队，请检查后重试~"]
    url = data["data"]["url"]
    return url

async def calculate_(): # 日常预测
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    final_url = f"https://www.jx3api.com/view/active/calculate?token={token}&robot={bot}"
    data = await get_api(final_url, proxy = proxies)
    url = data["data"]["url"]
    return url

async def flower_(flower: str = None, server: str = None): # 鲜花价格 <服务器> [花]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/home/flower?token={token}&robot={bot}&server={server}&name="
    if flower != None:
        final_url = final_url + flower
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def demon_(server: str = None): # 金价 <服务器>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if server == None:
        final_url = f"https://www.jx3api.com/view/trade/server/demon?robot={bot}&token={token}"
    else:
        server = server_mapping(server)
        if server == False:
            return ["唔……服务器名输入错误。"]
        final_url = f"https://www.jx3api.com/view/trade/demon?server={server}&robot={bot}&token={token}"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 401:
        return ["服务器名输入错误，请检查后重试~"]
    return data["data"]["url"]

async def item_(name: str = None): # 物价 <物品>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    final_url = f"https://www.jx3api.com/view/trade/search?token={token}&robot={bot}&name={name}"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return ["唔……尚未收录该物品。"]
    return data["data"]["url"]

async def serendipity_(server: str = None, name: str = None): # 角色奇遇 <服务器> <ID>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/lucky/serendipity?token={token}&robot={bot}&ticket={ticket}&server={server}&name={name}"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def statistical_(server: str = None, serendipity: str = None): # 近期奇遇 <服务器> [奇遇]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    if serendipity == None:
        final_url = f"https://www.jx3api.com/view/lucky/collect?token={token}&robot={bot}&server={server}"
    else:
        final_url = f"https://www.jx3api.com/view/lucky/statistical?token={token}&robot={bot}&ticket={ticket}&server={server}&name={serendipity}"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def global_serendipity(name: str = None): # 全服奇遇 [奇遇]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if name != None:
        final_url = f"https://www.jx3api.com/view/lucky/server/serendipity?name={name}&token={token}&robot={bot}"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def global_statistical(name: str = None): # 全服统计 [奇遇]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if name != None:
        final_url = f"https://www.jx3api.com/view/lucky/server/statistical?name={name}&token={token}&robot={bot}"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def addritube_(server: str = None, name: str = None): # 查装 <服务器> <ID>
    if token == None or ticket == None:
        return ["Bot尚未填写Ticket或Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/role/attribute?ticket={ticket}&token={token}&robot={bot}&server={server}&name={name}"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return ["唔……玩家不存在。"]
    if data["code"] == 403 and data["msg"] == "侠客隐藏了游戏信息":
        return ["唔，该玩家隐藏了信息。"]
    if data["code"] == 403 and data["msg"] == "仅互关好友可见":
        return ["仅互关好友可见哦~"]
    return data["data"]["url"]

async def firework_(server: str = None, name: str = None): # 烟花 <服务器> <ID>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/role/firework?token={token}&robot={bot}&server={server}&name={name}"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return ["该玩家没有烟花记录哦~"]
    return data["data"]["url"]

async def sandbox_(server: str = None): # 沙盘 <服务器>
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    if server != None:
        final_url = f"https://www.jx3api.com/view/sand/search?server=" + server
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 401:
        return ["唔……服务器名输入错误。"]
    return data["data"]["url"]

async def achievements_(server: str = None, name: str = None, achievement: str = None):
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if ticket == None:
        return ["Bot尚未填写Ticket，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/data/role/achievement?ticket={ticket}&token={token}&server={server}&role={name}&name={achievement}"
    data = await get_api(final_url, proxy = proxies)
    logger.info(data)
    if data["code"] == 401 or data["code"] == 404:
        return ["角色或成就不存在哦~"]
    node = []
    for i in data["data"]["data"]:
        icon = ms.image(i["icon"])
        name = i["name"]
        desc = i["desc"]
        point = i["rewardPoint"]
        isFinished = i["isFinished"]
        msg = icon + f"\n{name}\n{desc}\n资历：{point}点\n"
        if isFinished:
            msg = msg + "状态：已完成"
        else:
            msg = msg + "状态：尚未完成"
        node.append(nodetemp("团本成就",Config.bot[0],msg))
    if len(node) == 0:
        return ["未找到该副本的成就哦，或许试试单成就搜索？"]
    return {"result":node}

async def special_(server: str, item: str = None):
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    if item != None:
        final_url = f"https://www.jx3api.com/view/team/items/statistical?token={token}&server={server}&name={item}&robot={bot}"
    else:
        final_url = f"https://www.jx3api.com/view/team/items/collect?token={token}&server={server}&robot={bot}"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 401:
        return ["唔……服务器名输入错误。"]
    if data["code"] == 404:
        return ["唔……未找到该物品。"]
    return data["data"]["url"]

async def arena_(object: str, server: str = None, name: str = None, mode: str = "33"):
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if ticket == None:
        return ["Bot尚未填写Ticket，请联系Bot主人~"]
    if object == "战绩":
        server = server_mapping(server)
        if server == False:
            return ["唔……服务器名输入错误。"]
        final_url = f"https://www.jx3api.com/view/arena/recent?token={token}&name={name}&server={server}&robot={bot}&ticket={ticket}"
        data = await get_api(final_url, proxy = proxies)
        if data["code"] == 401:
            return ["唔……服务器名输入错误。"]
        if data["code"] == 404:
            return ["唔……未找到该玩家的记录，请检查玩家名或服务器名。"]
        return data["data"]["url"]
    elif object == "排行":
        final_url = f"https://www.jx3api.com/view/arena/awesome?token={token}&robot={bot}&ticket={ticket}&mode={mode}"
        data = await get_api(final_url, proxy = proxies)
        if data["code"] == 401:
            return ["唔……名剑模式输入错误。"]
        return data["data"]["url"]
    elif object == "统计":
        final_url = f"https://www.jx3api.com/view/arena/schools?token={token}&robot={bot}&ticket={ticket}&mode={mode}"
        data = await get_api(final_url, proxy = proxies)
        if data["code"] == 401:
            return ["唔……名剑模式输入错误。"]
        return data["data"]["url"]

async def trials_(server: str = None, school: str = None):
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if ticket == None:
        return ["Bot尚未填写Ticket，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/rank/trials?server={server}&school={school}&token={token}&robot={bot}"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 401:
        return ["唔……服务器名输入错误。"]
    if data["code"] == 404:
        return ["唔……门派名称输入错误。"]
    return data["data"]["url"]

async def rank_(type_1: str, type_2: str, server: str):
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if type_1 == "个人":
        if type_2 not in ["名士五十强","老江湖五十强","兵甲藏家五十强","名师五十强","阵营英雄五十强","薪火相传五十强","庐园广记一百强"]:
            return ["唔……类型不正确，请检查后重试~"]
        final_url = f"https://www.jx3api.com/view/rank/various?token={token}&robot={bot}&server={server}&type={type_2}"
    elif type_1 == "帮会":
        if type_2 not in ["浩气神兵宝甲五十强","恶人神兵宝甲五十强","浩气爱心帮会五十强","恶人爱心帮会五十强"]:
            return ["唔……类型不正确，请检查后重试~"]
        final_url = f"https://www.jx3api.com/view/rank/tribe?token={token}&robot={bot}&server={server}&type={type_2}"
    elif type_1 == "战功":
        if type_2 not in ["赛季恶人五十强","赛季浩气五十强","上周恶人五十强","上周浩气五十强","本周恶人五十强","本周浩气五十强"]:
            return ["唔……类型不正确，请检查后重试~"]
        final_url = f"https://www.jx3api.com/view/rank/excellent?token={token}&robot={bot}&server={server}&type={type_2}"
    else:
        return ["未知类型，只能是个人/帮会/战功哦！"]
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 401:
        return ["唔……参数有误！"]
    if data["code"] == 404:
        return ["唔……未收录！"]
    return data["data"]["url"]

async def announce_():
    final_url = f"https://www.jx3api.com/view/web/announce?robot={bot}&token={token}"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

def server_mapping(server: str):
    if server in ["二合一","四合一","六合一","七合一","千岛湖","圣墓山","执子之手","平步青云","笑傲江湖","幽月轮","山雨欲来"]:
        return "幽月轮"
    elif server in ["剑胆琴心","煎蛋","剑胆"]:
        return "剑胆琴心"
    elif server in ["梦江南","双梦","如梦令","枫泾古镇"]:
        return "梦江南"
    elif server in ["斗转星移","金戈铁马","风雨同舟","大唐万象","姨妈","风雨","风雨大姨妈"]:
        return "斗转星移"
    elif server in ["长安城"]:
        return "长安城"
    elif server in ["电八","电信八区","绝代天骄","风骨霸刀"]:
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
        ......................./.1-017
    elif server in ["青梅煮酒","青梅"]:
        return "青梅煮酒"
    elif server in ["横刀断浪","横刀"]:
        return "横刀断浪"
    elif server in ["破阵子","念破"]:
        return "破阵子"
    elif server in ["飞龙在天","飞龙"]:
        return "飞龙在天"
    else:
        return False

from fastapi import FastAPI
app: FastAPI = nonebot.get_app()

@app.get("/token") # `jx3`提交token的位置。
async def recToken(token: str = None, qq: str = None):
    if token == None:
        return {"status":404,"msg":"没有找到您提交的token哦，请检查您的链接是否有误！如果有不懂的请查询文档或询问作者(QQ:3349104868)！"}
    if qq == None:
        return {"status":404,"msg":"没有找到您提交的QQ号哦，请检查您的链接是否有误！如果有不懂的请查询文档或询问作者(QQ:3349104868)！"}
    else:
        now = json.loads(read(TOOLS + "/token.json"))
        for i in now:
            if i["qq"] == qq:
                old_ = i["token"]
                i["token"] = token
                write(TOOLS + "/token.json", json.dumps(now))
                return {"status":200,"msg":"已经更新你的token啦！如果你是不小心更改的，请根据这里附带的旧token，重新拼接url并访问哦~","old_token":old_}
        new = {"qq":qq, "token":token}
        now.append(new)
        write(TOOLS + "/token.json", json.dumps(now))
        return {"status":200,"msg":"已为你存储token，请记住，只有您提交的QQ拥有访问部分功能的权限，他人无法查看哦~"}