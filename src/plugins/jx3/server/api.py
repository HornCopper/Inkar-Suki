from src.tools.dep import *


async def server_status(server: str = None):
    server = server_mapping(server)
    full_link = "{Config.jx3api_link}/data/server/check?server=" + server
    info = await get_api(full_link, proxy=proxies)
    try:
        all_servers = info["data"]
        if str(type(all_servers)).find("list") != -1:
            return "服务器名输入错误。"
    except:
        pass
    status = info["data"]["status"]
    if status == 1:
        return f"开服状态：{server}已开服。"
    elif status == 0:
        return f"开服状态：{server}维护中。"
