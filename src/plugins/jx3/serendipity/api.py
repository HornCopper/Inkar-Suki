from src.tools.basic import *

from src.tools.generate import generate, get_uuid
from src.plugins.help import css

from bs4 import BeautifulSoup


async def serendipity_(server: str = None, name: str = None, group_id: str = None):  # 奇遇 <服务器> <ID>
    if token is None:
        return [PROMPT_NoToken]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    final_url = f"{Config.jx3api_link}/view/luck/adventure?token={token}&robot={bot}&ticket={ticket}&server={server}&name={name}&scale=1"
    data = await get_api(final_url)
    return data["data"]["url"]


# 近期奇遇 <服务器> [奇遇]
async def statistical_(server: str = None, serendipity: str = None, group_id: str = None):
    if token is None:
        return [PROMPT_NoToken]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    if serendipity is None:
        final_url = f"{Config.jx3api_link}/view/luck/collect?token={token}&robot={bot}&server={server}&scale=1"
    else:
        final_url = f"{Config.jx3api_link}/view/luck/statistical?token={token}&robot={bot}&ticket={ticket}&server={server}&name={serendipity}&scale=1"
    data = await get_api(final_url)
    return data["data"]["url"]


async def global_serendipity(name: str = None):  # 全服奇遇 [奇遇]
    if token is None:
        return [PROMPT_NoToken]
    if name is not None:
        final_url = f"{Config.jx3api_link}/view/luck/server/adventure?name={name}&token={token}&robot={bot}&scale=1"
    data = await get_api(final_url)
    return data["data"]["url"]


async def global_statistical(name: str = None):  # 全服统计 [奇遇]
    if token is None:
        return [PROMPT_NoToken]
    if name is not None:
        final_url = f"{Config.jx3api_link}/view/luck/server/statistical?name={name}&token={token}&robot={bot}"
    data = await get_api(final_url)
    return data["data"]["url"]

addtional_css = """
.m-wiki-metas .c-header .m-adventure-navigation
{
    display: none;
}
"""

async def get_preposition(name: str = None):
    url = "https://inkar-suki.codethink.cn/serendipity"
    data = await get_api(url)
    flag = False
    for i in data:
        if i["name"] == name:
            id = i["id"]
            flag = True
    if not flag:
        return False
    final_url = "https://jx3box.com/adventure/" + str(id)
    image = await generate(final_url, True, ".c-wiki-panel", True, 4000, addtional_css)
    return Path(image).as_uri()