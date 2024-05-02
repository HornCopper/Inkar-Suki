from bs4 import BeautifulSoup

from src.tools.utils import get_url, get_api
from src.tools.basic import *

from ..jx3 import server_mapping


async def get_horse_reporter(server: str, group_id: str = None):  # 数据来源@JX3BOX
    server = server_mapping(server, group_id)
    if not server:
        return PROMPT_ServerNotExist
    final_url = f"https://next2.jx3box.com/api/game/reporter/horse?type=horse&server={server}"
    data = await get_api(final_url)
    if data["data"]["page"]["total"] == 0:
        return "没有找到该服务器信息哦，请检查后重试~"
    for i in data["data"]["list"]:
        if i["subtype"] == "npc_chat":
            time_ = convert_time(i["time"], "%m-%d %H:%M:%S")
            content = i["content"]
            map = i["map_name"]
            msg = f"{content}\n刷新时间：{time_}\n地图：{map}"
            return msg
