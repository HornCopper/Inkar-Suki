from src.tools.dep.api import *
from src.tools.dep.server import *
from src.constant.jx3 import *

async def daily_(server: str = None):
    server = server_mapping(server)
    if server == False:
        return [PROMPT_ServerNotExist]
    full_link = f"https://www.jx3api.com/view/active/current?robot={bot}&server={server}"
    data = await get_api(full_link, proxy = proxies)
    return data["data"]["url"]