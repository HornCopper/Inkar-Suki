from typing import Literal

from src.config import Config
from src.const.jx3.server import Server
from src.utils.network import Request
from src.utils.database.classes import RoleData

async def get_role_card_url(role_data: RoleData) -> tuple[str, int] | Literal[False]:
    _server = Server(role_data.serverName)
    params = {
        "game_global_role_id": role_data.globalRoleId,
        "game_role_id": role_data.roleId,
        "zone": _server.zone,
        "server": _server.server
    }
    tuilan_data = (await Request("https://m.pvp.xoyo.com/badge/get-role-card-preset", params=params).post(tuilan=True)).json()
    if tuilan_data["code"] != 0:
        return False
    unsecret_request = Request(f"{Config.jx3.api.cqc_url}/role_card", params={"showCardPresetUrl": tuilan_data["data"]["showCardPresetUrl"]})
    data = await unsecret_request.get()
    # 防的就是蓉蓉，别问
    return data.json()["url"], tuilan_data["data"]["praiseTotalCount"]
