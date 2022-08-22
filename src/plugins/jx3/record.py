import sys
import nonebot

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import get_api, convert_time, nodetemp
from config import Config

async def adventure____(id: str, server: str = "幽月轮"):
    final_url = f"https://www.jx3pd.com/api/serendipity?server={server}&type=%E4%B8%8D%E9%99%90&serendipity=%E4%B8%8D%E9%99%90&name={id}&limit=200"
    data = await get_api(final_url)
    if len(data["data"]) == 0:
        return []
    node = []
    for i in data["data"]:
        if i["time"] == 0:
            time = "过去太久了或者没有记录到哦~"
        else:
            time = convert_time(i["time"])
        server = i["server"]
        name = i["serendipity"]
        id = i["name"]
        node.append(nodetemp("奇遇查询", Config.bot[0], f"服务器：{server}\n角色：{id}\n奇遇：{name}\n时间：{time}"))
    return node

async def firework(id: str, server: str = "幽月轮"):
    final_url = f"https://www.jx3pd.com/api/firework?server={server}&name={id}"
    data = await get_api(final_url)
    if len(data["data"]) == 0:
        return []
    node = []
    for i in data["data"]:
        if i["time"] == 0:
            time = "过去太久了或者没有记录到哦~"
        else:
            time = convert_time(i["time"])
        server = i["server"]
        firework_name = i["name"]
        map = i["map"]
        sender = i["sender"]
        receiver = i["recipient"]
        node.append(nodetemp("烟花查询", Config.bot[0], f"服务器：{server}\n时间：{time}\n{sender}在{map}对{receiver}使用了传说中的{firework_name}。"))
    return node