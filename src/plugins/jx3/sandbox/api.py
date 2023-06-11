from src.tools.dep.api import *
from src.tools.dep.server import *

async def sandbox_(server: str = None): # 沙盘 <服务器>
    server = server_mapping(server)
    if server == False:
        return [PROMPT_ServerInvalid]
    if server != None:
        final_url = f"https://www.jx3api.com/view/server/sand?token={token}&scale=1&robot={bot}&server=" + server
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 400:
        return [PROMPT_ServerInvalid]
    return data["data"]["url"]