from src.tools.dep.api import *
from src.tools.dep.server import *

async def serendipity_(server: str = None, name: str = None): # 奇遇 <服务器> <ID>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/luck/adventure?token={token}&robot={bot}&ticket={ticket}&server={server}&name={name}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def statistical_(server: str = None, serendipity: str = None): # 近期奇遇 <服务器> [奇遇]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    if serendipity == None:
        final_url = f"https://www.jx3api.com/view/luck/collect?token={token}&robot={bot}&server={server}&scale=1"
    else:
        final_url = f"https://www.jx3api.com/view/luck/statistical?token={token}&robot={bot}&ticket={ticket}&server={server}&name={serendipity}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def global_serendipity(name: str = None): # 全服奇遇 [奇遇]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if name != None:
        final_url = f"https://www.jx3api.com/view/luck/server/adventure?name={name}&token={token}&robot={bot}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]

async def global_statistical(name: str = None): # 全服统计 [奇遇]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if name != None:
        final_url = f"https://www.jx3api.com/view/luck/server/statistical?name={name}&token={token}&robot={bot}"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]