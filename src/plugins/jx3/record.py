import sys
import nonebot
import time

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import get_api, nodetemp
from config import Config

async def adventure____(id: str = None, server: str = "幽月轮"):
    final_url = f"https://www.jx3mm.com/home/qyinfo?m=1&S={server}&n={id}"
    if id == None:
        final_url = f"https://www.jx3mm.com/home/qyinfo?m=1&S={server}"
    data = await get_api(final_url)
    if len(data["result"]) == 0:
        return []
    node = []
    for i in data["result"]:
        if i["time"] == 0:
            time_ = "过去太久了或者没有记录到哦~"
        else:
            timeArray = time.localtime(i["time"])
            time_ = time.strftime("%Y年%m月%d日%H:%M:%S", timeArray)
        server = i["server"]
        name = i["serendipity"]
        id = i["name"]
        node.append(nodetemp("奇遇查询", Config.bot[0], f"服务器：{server}\n角色：{id}\n奇遇：{name}\n时间：{time_}"))
    return node

async def firework(id: str = None, server: str = "幽月轮"):
#     final_url = f"https://www.jx3pd.com/api/firework?server={server}&name={id}"
#     if id == None:
#         final_url = f"https://www.jx3pd.com/api/firework?server={server}&name={id}"
#     data = await get_api(final_url)
#     if len(data["data"]) == 0:
#         return []
#     node = []
#     for i in data["data"]:
#         if i["time"] == 0:
#             time_ = "过去太久了或者没有记录到哦~"
#         else:
#             timeArray = time.localtime(i["time"])
#             time_ = time.strftime("%Y年%m月%d日%H:%M:%S", timeArray)
#         server = i["server"]
#         firework_name = i["name"]
#         map = i["map"]
#         sender = i["sender"]
#         receiver = i["recipient"]
#         node.append(nodetemp("烟花查询", Config.bot[0], f"服务器：{server}\n时间：{time_}\n{sender}在{map}对{receiver}使用了传说中的{firework_name}。"))
#     return node 
    pass