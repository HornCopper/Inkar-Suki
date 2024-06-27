from src.tools.basic import *


async def server_status(server: str = None):
    full_link = f"{Config.jx3api_link}/data/server/check"
    info = await get_api(full_link)
    data = info["data"]
    prefix = "开服状态："
    for i in data:
        if i["server"] == server:
            status_desc = "已开服。" if i["status"] else "维护中。"
    msg = f"{prefix} {server} {status_desc}"
    return msg
