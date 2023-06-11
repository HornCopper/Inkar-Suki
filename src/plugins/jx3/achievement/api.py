from src.tools.dep.api import *
from src.tools.dep.server import *
from .adventure import *

async def achievements_(server: str = None, name: str = None, achievement: str = None):
    if token == None:
        return [PROMPT_NoToken]
    if ticket == None:
        return [PROMPT_NoTicket]
    server = server_mapping(server)
    if server == False:
        return [PROMPT_ServerInvalid]
    final_url = f"https://www.jx3api.com/view/role/achievement?server={server}&name={achievement}&role={name}&robot={bot}&ticket={ticket}&token={token}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 400:
        return [PROMPT_ServerInvalid]
    if data["data"] == {}:
        return ["唔……未找到相应成就。"]
    if data["code"] == 404:
        return ["唔……玩家名输入错误。"]
    return data["data"]["url"]