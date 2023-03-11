from bs4 import BeautifulSoup
import nonebot
import sys

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)

from utils import get_url
from .jx3 import server_mapping

async def get_chitu(server: str, group: str):
    api = "https://jw3cx.com/"
    data = await get_url(api)
    server = server_mapping(server, group)
    if server == False:
        return "唔……服务器名输入有误，请检查后重试~"
    bs_obj_data = BeautifulSoup(data, "html.parser")
    info = bs_obj_data.find_all(onchange="show_input();")[0].find_all("option")
    for i in info:
        if i["value"].find(server) != -1:
            return f"{server}：{i.get_text()}"
    return "唔……服务器名输入有误，请检查后重试~"
        