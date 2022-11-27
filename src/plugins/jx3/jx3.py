import nonebot
import sys

from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.log import logger

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import get_api, nodetemp
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

async def server_status(server_name):
    full_link = "https://www.jx3api.com/data/server/check?server="+server_name
    info = await get_api(full_link, proxy = proxies)
    try:
        all_servers = info["data"]
        if str(type(all_servers)).find("list") != -1:
            return "服务器名输入错误。"
    except:
        pass
    status = info["data"]["status"]
    if status == 1:
        return f"{server_name}服务器状态正常。"
    elif status == 0:
        return f"{server_name}服务器维护中。"

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
    
async def daily_(server):
    full_link = "https://www.jx3api.com/data/active/current?server=" + server
    info = await get_api(full_link, proxy = proxies)
    date = info["data"]["date"]
    week = info["data"]["week"]
    war = info["data"]["war"]
    battle = info["data"]["battle"]
    camp = info["data"]["camp"]
    prestige = info["data"]["prestige"]
    prestige = "，".join(prestige)
    relief = "驰援" + info["data"]["relief"][0:1]
    school = info["data"]["school"]
    try:
        draw_obj = info["data"]["draw"]
    except:
        draw_obj = "无（周三、周五、周末才有哦~）"
    weekly_war = info["data"]["team"][1].replace(";","，")
    weekly_big_war = info["data"]["team"][2].replace(";","，")
    weekly_task = info["data"]["team"][0].replace(";","，")
    return f"查到该区服（{date}，周{week}）的信息啦！\n大战：大战！{war}！\n矿车阵营日常：跨服·{camp}！\n驰援任务：{relief}\n战场：{battle}\n美人图：{draw_obj}\n世界公共任务：{weekly_task}\n小队秘境周常：{weekly_war}\n团队秘境周常：{weekly_big_war}\n家园声望秘境：{prestige}\n门派事件：{school}"

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
    final_url = f"https://www.jx3api.com/view/team/member/recruit?token={token}&server={server}&robot={bot}&keyword="
    if copy != None:
        final_url = final_url + copy
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 403:
        return ["Token不正确哦，请联系Bot主人~"]
    elif data["code"] == 401:
        return ["服务器名输入错误，请检查后重试~"]
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
    final_url = f"https://www.jx3api.com/view/lucky/serendipity?token={token}&robot={bot}&ticket={ticket}&server={server}&name={name}"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def statistical_(server: str = None, serendipity: str = None): # 近期奇遇 <服务器> [奇遇]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
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
    final_url = f"https://www.jx3api.com/view/role/attribute?ticket={ticket}&token={token}&robot={bot}&server={server}&name={name}"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return ["唔……玩家不存在。"]
    if data["code"] == 403 and data["msg"] == "侠客隐藏了游戏信息":
        return ["唔，该玩家隐藏了信息。"]
    return data["data"]["url"]

async def firework_(server: str = None, name: str = None): # 烟花 <服务器> <ID>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    final_url = f"https://www.jx3api.com/view/role/firework?token={token}&robot={bot}&server={server}&name={name}"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return ["该玩家没有烟花记录哦~"]
    return data["data"]["url"]

async def sandbox_(server: str = None): # 沙盘 <服务器>
    if server != None:
        final_url = f"https://www.jx3api.com/view/sand/search?server=" + server
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 401:
        return ["唔……服务器名输入错误。"]
    return data["data"]["url"]
