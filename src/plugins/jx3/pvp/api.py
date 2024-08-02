from src.tools.basic.msg import PROMPT
from src.tools.config import Config
from src.tools.basic.data_server import server_mapping
from src.tools.utils.request import get_api

token = Config.jx3.api.token
ticket = Config.jx3.api.ticket
bot_name = Config.bot_basic.bot_name_argument

async def arena_record(server: str = None, name: str = None, mode: str = "", group_id: str = None):
    if token == None:
        return [PROMPT.NoToken]
    if ticket == None:
        return [PROMPT.NoTicket]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    final_url = f"{Config.jx3.api.url}/view/match/recent?token={token}&name={name}&server={server}&nickname={bot_name}&ticket={ticket}&mode={mode}&chrome=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return [PROMPT.ServerInvalid]
    if data["code"] == 404:
        return [f"唔……未找到该玩家，请提交角色！\n提交角色 服务器 UID"]
    return data["data"]["url"]

async def arena_rank(mode: str = "33"):
    final_url = f"{Config.jx3.api.url}/view/match/awesome?token={token}&nickname={bot_name}&ticket={ticket}&mode={mode}&chrome=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return ["唔……名剑模式输入错误。"]
    return data["data"]["url"]

async def arena_stastic(mode: str = "33"):
    final_url = f"{Config.jx3.api.url}/view/match/schools?token={token}&nickname={bot_name}&ticket={ticket}&mode={mode}&chrome=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return ["唔……名剑模式输入错误。"]
    return data["data"]["url"]