from src.config import Config
from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.decorators import token_required
from src.utils.network import Request
from src.utils.database.player import search_player

@token_required
async def get_role_info(server: str, name: str, token: str = ""):
    params = {
        "token": token,
        "name": name,
        "server": server
    }
    url = f"{Config.jx3.api.url}/role/detail"
    data = (await Request(url, params=params).get()).json()
    if data["code"] == 404:
        return "没有找到该玩家哦~\n需要该玩家在世界频道发言后方可查询。"
    msg = "以下信息仅供参考！\n数据可能已经过期，但UID之类的仍可参考。"
    _zone = data["data"]["zoneName"]
    _server = data["data"]["serverName"]
    _name = data["data"]["roleName"]
    _role_id = data["data"]["roleId"]
    _force_name = data["data"]["forceName"]
    _body_name = data["data"]["bodyName"]
    _tong_name = data["data"]["tongName"]
    _camp_name = data["data"]["campName"]
    _global_role_id = data["data"]["globalId"]
    msg = msg + f"\n服务器：{_zone} - {_server}\n角色名称：{_name}\n标识：{_role_id}\n体型：{_force_name}·{_body_name}\n帮会：{_camp_name} - {_tong_name}\n全服标识：{_global_role_id}"
    return msg

async def get_online_info(server: str, name: str) -> str:
    role_info = await search_player(role_name=name, server_name=server)
    if not role_info.roleId:
        return PROMPT.PlayerNotExist
    url = f"{Config.jx3.api.cqc_url}/role_online"
    params = {
        "zone": Server(server).zone or "",
        "server": server,
        "name": name,
        "role_id": role_info.roleId,
        "global_role_id": role_info.globalRoleId,
        "token": Config.jx3.api.ticket
    }
    data = (await Request(url, params=params).get()).json()
    status = bool(data["data"][0]["gameLogin"])
    key = "在线" if status else "离线"
    return f"[{name}·{server}] 当前{key}"