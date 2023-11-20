from src.tools.dep import *


async def demon_(server: str = None, group_id: str = None):  # 金价 <服务器>
    if token == None:
        return [PROMPT_NoToken]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    final_url = f"{Config.jx3api_link}/view/trade/demon?robot={bot}&server={server}&scale=1&token={token}"
    data = await get_api(final_url)
    if data["code"] == 400:
        return ["服务器名输入错误，请检查后重试~"]
    return data["data"]["url"]
