from bs4 import BeautifulSoup
import nonebot
import time
import sys

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import get_url, get_api
from .jx3 import server_mapping

async def get_chitu(server: str, group: str): # 数据来源@jw3cx.com
    api = "https://jw3cx.com/"
    data = await get_url(api)
    server = server_mapping(server, group)
    if server == False:
        return "唔……服务器名输入有误，请检查后重试~"
    bs_obj_data = BeautifulSoup(data, "html.parser")
    info = bs_obj_data.find_all(onchange="show_input();")[0].find_all("option")
    for i in info:
        if i.get_text().find(server) != -1:
            return f"{i.get_text()}：" + i["value"]
    return "唔……服务器名输入有误，请检查后重试~"

async def get_horse_reporter(server: str, group: str): #数据来源@JX3BOX
    server = server_mapping(server, group)
    if server == False:
        return "没有找到该服务器哦，请检查后重试~"
    final_url = f"https://next2.jx3box.com/api/game/reporter/horse?type=horse&server={server}"
    data = await get_api(final_url)
    if data["data"]["page"]["total"] == 0:
        return "没有找到该服务器信息哦，请检查后重试~"
    for i in data["data"]["list"]:
        if i["subtype"] == "npc_chat":
            time_ = time.strftime("%Y年%m月%d日 %H:%M:%S", time.localtime(i["time"]))
            content = i["content"]
            map = i["map_name"]
            msg = f"{content}\n刷新时间：{time_}\n地图：{map}"
            return msg
