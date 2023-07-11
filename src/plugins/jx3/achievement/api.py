from src.tools.dep import *

from .adventure import *

async def achievements_(server: str = None, name: str = None, achievement: str = None, group_id: str = None):
    if token == None:
        return [PROMPT_NoToken]
    if ticket == None:
        return [PROMPT_NoTicket]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    final_url = f"{Config.jx3api_link}/view/role/achievement?server={server}&name={achievement}&role={name}&robot={bot}&ticket={ticket}&token={token}&scale=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return [PROMPT_ServerInvalid]
    if data["data"] == {}:
        return ["唔……未找到相应成就。"]
    if data["code"] == 404:
        return ["唔……玩家名输入错误。"]
    return data["data"]["url"]
