from src.tools.dep.api import *
from src.tools.dep.server import *
from src.constant.jx3 import *


async def daily_(server: str = None, group_id: str = None):
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    full_link = f"https://www.jx3api.com/view/active/current?robot={bot}&server={server}"
    data = await get_api(full_link, proxy=proxies)
    return data["data"]["url"]
