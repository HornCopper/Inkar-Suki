from src.tools.basic import *


async def server_status(server: str = None):
    full_link = f"{Config.jx3api_link}/data/server/check?server={server}&token={token}"
    info = await get_api(full_link)
    data = info["data"]
    prefix = "开服状态："
    status_desc = "已开服。" if data["status"] else "维护中。"
    msg = f"{prefix} {server.name} {status_desc}"
    return msg
