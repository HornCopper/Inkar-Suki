from src.config import Config
from src.utils.decorators import token_required
from src.utils.network import Request

@token_required
async def get_role_info(server: str, name: str, token: str = ""):
    final_url = f"{Config.jx3.api.url}/data/role/detailed?token={token}&name={name}&server={server}"
    data = (await Request(final_url).get()).json()
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
    _person_id = data["data"]["personId"]
    _global_role_id = data["data"]["globalRoleId"]
    msg = msg + f"\n服务器：{_zone} - {_server}\n角色名称：{_name}\n标识：{_role_id}\n体型：{_force_name}·{_body_name}\n帮会：{_camp_name} - {_tong_name}\n账号标识：{_person_id}\n全服标识：{_global_role_id}"
    return msg