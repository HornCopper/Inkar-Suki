import nonebot
import time
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
        heighten_food = info["heighten_food"]
        auxiliary_food = info["auxiliary_food"]
        heighten_drug = info["heighten_drug"]
        auxiliary_drug = info["auxiliary_drug"]
        return f"查到{name}的推荐小药了：\n增强食品：{heighten_food}\n辅助食品：{auxiliary_food}\n增强药品：{heighten_drug}\n辅助药品：{auxiliary_drug}"

async def price_(name): # API 3.0 数据较为实用，暂不更新
    full_link = "https://api.jx3api.com/app/price?name=" + name
    data = await get_api(full_link, proxy = proxies)
    if data["code"] == 401:
        return "此外观不存在哦~请检查后重试。"
    else:
        info = data["data"]
        name = info["name"]
        info_ = info["info"]
        img = ms.image(info["upload"])
        msg = f"{name}\n{info_}\n" + img + "\n"
        each_srv = info["data"]
        def zsdpt(zone, server, date, price, type_):
            if type_ == "收入":
                return f"{zone}-{server}\n{date}：￥{price}收。"
            else:
                return f"{zone}-{server}\n{date}：￥{price}出。"
        for i in each_srv[0]:
            if len(i) == 0:
                continue
            else:
                zone = i["zone"]
                server = i["server"]
                price = str(i["value"])
                sale = i["sale"]
                date = i["date"]
                msg = msg + "\n" + zsdpt(zone, server, date, price, sale)
        return msg

async def demon_(name):
    full_link = "https://www.jx3api.com/data/trade/demon?server=" + name
    data = await get_api(full_link, proxy = proxies)
    lastest = data["data"][0]
    if lastest["server"] != name:
        return "此服务器不存在哦~请检查后重试。"
    else:
        wbl = lastest["wanbaolou"]
        tb = lastest["tieba"]
        dd = lastest["dd373"]
        uu = lastest["uu898"]
        _5173 = lastest["5173"]
        _7881 = lastest["7881"]
        date = lastest["date"]
        return f"查到区服{name}{date}的金价信息：\n万宝楼：{wbl}\n贴吧：{tb}\nDD373：{dd}\nUU898：{uu}\n5173：{_5173}\n7881：{_7881}"

async def tiangou_():
    full_link = "https://www.jx3api.com/data/useless/flatterer"
    data = await get_api(full_link, proxy = proxies)
    text = data["data"]["text"]
    return text

async def recruit_(server: str, copy: str = None):
    token = Config.jx3api_recruittoken
    if token == None:
        return "Bot尚未填写Token，请联系Bot主人~"
    final_url = f"https://www.jx3api.com/view/team/member/recruit?token={token}&server={server}&robot=Inkar-Suki&&keyword="
    if copy != None:
        final_url = final_url + copy
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 403:
        return ["Token不正确哦，请联系Bot主人~"]
    elif data["code"] == 401:
        return ["服务器名输入错误，请检查后重试~"]
    url = data["data"]["url"]
    return url