from src.tools.basic import *


async def arena_record(server: str = None, name: str = None, mode: str = "", group_id: str = None):
    if token == None:
        return [PROMPT_NoToken]
    if ticket == None:
        return [PROMPT_NoTicket]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    final_url = f"{Config.jx3.api.url}/view/match/recent?token={token}&name={name}&server={server}&nickname={bot}&ticket={ticket}&mode={mode}&chrome=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return [PROMPT_ServerInvalid]
    if data["code"] == 404:
        return ["唔……未找到该玩家的记录，请检查玩家名或服务器名。"]
    return data["data"]["url"]

async def arena_rank(mode: str = "33"):
    final_url = f"{Config.jx3.api.url}/view/match/awesome?token={token}&nickname={bot}&ticket={ticket}&mode={mode}&chrome=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return ["唔……名剑模式输入错误。"]
    return data["data"]["url"]

async def arena_stastic(mode: str = "33"):
    final_url = f"{Config.jx3.api.url}/view/match/schools?token={token}&nickname={bot}&ticket={ticket}&mode={mode}&chrome=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return ["唔……名剑模式输入错误。"]
    return data["data"]["url"]