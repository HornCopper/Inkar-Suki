from src.tools.dep import *

from src.tools.generate import generate, get_uuid
from src.plugins.help import css

from bs4 import BeautifulSoup


async def serendipity_(server: str = None, name: str = None, group_id: str = None):  # 奇遇 <服务器> <ID>
    if token == None:
        return [PROMPT_NoToken]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    final_url = f"{Config.jx3api_link}/view/luck/adventure?token={token}&robot={bot}&ticket={ticket}&server={server}&name={name}&scale=1"
    data = await get_api(final_url)
    return data["data"]["url"]


# 近期奇遇 <服务器> [奇遇]
async def statistical_(server: str = None, serendipity: str = None, group_id: str = None):
    if token == None:
        return [PROMPT_NoToken]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    if serendipity == None:
        final_url = f"{Config.jx3api_link}/view/luck/collect?token={token}&robot={bot}&server={server}&scale=1"
    else:
        final_url = f"{Config.jx3api_link}/view/luck/statistical?token={token}&robot={bot}&ticket={ticket}&server={server}&name={serendipity}&scale=1"
    data = await get_api(final_url)
    return data["data"]["url"]


async def global_serendipity(name: str = None):  # 全服奇遇 [奇遇]
    if token == None:
        return [PROMPT_NoToken]
    if name != None:
        final_url = f"{Config.jx3api_link}/view/luck/server/adventure?name={name}&token={token}&robot={bot}&scale=1"
    data = await get_api(final_url)
    return data["data"]["url"]


async def global_statistical(name: str = None):  # 全服统计 [奇遇]
    if token == None:
        return [PROMPT_NoToken]
    if name != None:
        final_url = f"{Config.jx3api_link}/view/luck/server/statistical?name={name}&token={token}&robot={bot}"
    data = await get_api(final_url)
    return data["data"]["url"]

async def get_preposition_page_url(name: str = None):
    api = "http://jx3yymj.com/index.php?mid=qy"
    data = await get_url(api)
    bs = BeautifulSoup(data, "html.parser")
    all = bs.find_all("li", class_="clear")
    for i in all:
        singlen = i.find(class_="ngeb").get_text()
        singleu = "http://jx3yymj.com/" + i.a["href"]
        if singlen.find(name) != -1:
            return singleu
    return False
        
async def get_preposition(name: str = None):
    url = await get_preposition_page_url(name)
    if url == False:
        return False
    data = await get_url(url)
    bs = BeautifulSoup(data, "html.parser")
    table = bs.find(class_ = "et_vars bd_tb")
    table = css + str(table).replace("<caption class=\"blind\">Extra Form</caption>", "")
    path = CACHE + "/" + get_uuid() + ".html"
    html = write(path, table)
    img = await generate(path, False, "table", False)
    return Path(img).as_uri()

async def get_image(name: str = None):
    url = await get_preposition_page_url(name)
    if url == False:
        return False
    data = await get_url(url)
    bs = BeautifulSoup(data, "html.parser")
    article = bs.find("article").find_all("img")[0]["src"]
    return article