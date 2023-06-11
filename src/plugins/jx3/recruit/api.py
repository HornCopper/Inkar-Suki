from src.tools.dep.api import *
from src.tools.dep.server import *

async def api_recruit(server: str, copy: str = ""):  # 团队招募 <服务器> [关键词]
    if token == None:
        return [PROMPT_NoToken]
    server = server_mapping(server)
    if not server:
        return [PROMPT_ServerInvalid]
    final_url = f"https://www.jx3api.com/view/member/recruit?token={token}&server={server}&robot={bot}&scale=1&keyword="
    if copy != "":
        final_url = final_url + copy
    data = await get_api(final_url, proxy=proxies)
    if data["code"] == 403:
        return [PROMPT_InvalidToken]
    elif data["code"] == 400:
        return [PROMPT_ServerNotExist]
    elif data["code"] == 404:
        return ["未找到相关团队，请检查后重试~"]
    url = data["data"]["url"]
    return url
