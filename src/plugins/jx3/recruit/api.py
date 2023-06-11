from src.tools.dep.api import *
from src.tools.dep.server import *

async def recruit_(server: str, copy: str = ""): # 团队招募 <服务器> [关键词]
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    server = server_mapping(server)
    if server == False:
        return ["唔……服务器名输入错误。"]
    final_url = f"https://www.jx3api.com/view/member/recruit?token={token}&server={server}&robot={bot}&scale=1&keyword="
    if copy != "":
        final_url = final_url + copy
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 403:
        return ["Token不正确哦，请联系Bot主人~"]
    elif data["code"] == 400:
        return ["服务器名输入错误，请检查后重试~"]
    elif data["code"] == 404:
        return ["未找到相关团队，请检查后重试~"]
    url = data["data"]["url"]
    return url
