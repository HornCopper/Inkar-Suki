from src.tools.dep.api import *
from src.tools.dep.server import *

async def demon_(server: str = None): # 金价 <服务器>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    if server == None:
        return ["服务器名输入错误，请检查后重试~"]
    else:
        server = server_mapping(server)
        if server == False:
            return ["唔……服务器名输入错误。"]
        final_url = f"https://www.jx3api.com/view/trade/demon?robot={bot}&server={server}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 400:
        return ["服务器名输入错误，请检查后重试~"]
    return data["data"]["url"]