from src.tools.dep.api import *
from src.tools.dep.server import *


async def demon_(server: str = None, group_id: str = None):  # 金价 <服务器>
    if token == None:
        return [PROMPT_NoToken]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    final_url = f"https://www.jx3api.com/view/trade/demon?robot={bot}&server={server}&scale=1"

    data = await get_api(final_url, proxy=proxies)
    if data["code"] == 400:
        return ["服务器名输入错误，请检查后重试~"]
    return data["data"]["url"]
