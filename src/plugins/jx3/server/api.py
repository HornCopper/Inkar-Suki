from src.tools.dep import *


async def server_status(server: str = None):
    server = server_mapping(server)
    full_link = f"{Config.jx3api_link}/data/server/check?server={server}&token={token}"
    info = await get_api(full_link)
    data = info and info.get('data')
    if isinstance(data, list):
        return "没有这样的服务器"
    status = data and data.get('status')
    prefix = "开服状态："
    if status == 1:
        return f"{prefix}{server}已开服。"
    elif status == 0:
        return f"{prefix}{server}维护中。"
    return f"{prefix}未能查询到服务状态"
