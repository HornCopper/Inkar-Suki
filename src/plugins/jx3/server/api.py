from src.tools.dep import *


async def server_status(server: str = None):
    server: Server = Server.from_alias(server)
    if server:
        full_link = f"{Config.jx3api_link}/data/server/check?server={server.name}&token={token}"
        info = await get_api(full_link)
        data = info and info.get("data")
    if server is None or isinstance(data, list):
        return "唔……服务器不存在哦，请检查后重试~"
    status = data and data.get("status")
    prefix = "开服状态："
    status_desc = "已开服。" if status else "维护中。"
    msg = f"{prefix} {server.name} {status_desc}"
    return msg
