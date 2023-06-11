from src.tools.dep.api import *
from src.tools.dep.server import *

async def arena_(object: str, server: str = None, name: str = None, mode: str = "33"):
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if ticket == None:
        return ["Bot尚未填写Ticket，请联系Bot主人~"]
    if object == "战绩":
        server = server_mapping(server)
        if server == False:
            return ["唔……服务器名输入错误。"]
        final_url = f"https://www.jx3api.com/view/match/recent?token={token}&name={name}&server={server}&robot={bot}&ticket={ticket}&mode={mode}&scale=1"
        data = await get_api(final_url, proxy = proxies)
        if data["code"] == 400:
            return ["唔……服务器名输入错误。"]
        if data["code"] == 404:
            return ["唔……未找到该玩家的记录，请检查玩家名或服务器名。"]
        return data["data"]["url"]
    elif object == "排行":
        final_url = f"https://www.jx3api.com/view/match/awesome?token={token}&robot={bot}&ticket={ticket}&mode={mode}&scale=1"
        data = await get_api(final_url, proxy = proxies)
        if data["code"] == 400:
            return ["唔……名剑模式输入错误。"]
        return data["data"]["url"]
    elif object == "统计":
        final_url = f"https://www.jx3api.com/data/match/schools?token={token}&robot={bot}&ticket={ticket}&mode={mode}&scale=1"
        data = await get_api(final_url, proxy = proxies)
        if data["code"] == 400:
            return ["唔……名剑模式输入错误。"]
        return data["data"]["url"]