from typing import Any

from src.config import Config
from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.network import Request
from src.utils.database import db
from src.utils.database.classes import RoleData
from src.utils.decorators import (
    ticket_required,
    token_required
)

try:
    from .uid import get_uid # type: ignore
    # 如果有能够获取UID的方法，请在这里提供
except:
    pass

@token_required
@ticket_required
async def get_uid(roleName: str, serverName: str, token: str, ticket: str):
    if Config.jx3.api.enable:
        data = (await Request(f"{Config.jx3.api.url}/data/role/detailed?token={token}&server={serverName}&name={roleName}&ticket={ticket}").get()).json()
        if data["code"] != 200:
            return None
        return data["data"]["roleId"]
    else:
        return None

async def get_uid_data(role_id: str = "", server: str = "") -> str | list:
    current_data: RoleData | Any = db.where_one(RoleData(), "roleId = ?", role_id, default=RoleData())
    if current_data.roleName != "":
        prefix = f"绑定成功！\n覆盖数据：[{current_data.roleName} · {current_data.serverName}] -> "
    else:
        prefix = f"绑定成功！\n记录数据："
    params = {
        "role_id": role_id,
        "zone": Server(server).zone,
        "server": server
    }
    data = (await Request("https://m.pvp.xoyo.com/role/indicator", params=params).post(tuilan=True)).json()
    data = data["data"]["role_info"]
    if data is None:
        return PROMPT.UIDInvalid
    data["bodyName"] = data.pop("body_type")
    data["campName"] = data.pop("camp")
    data["forceName"] = data.pop("force")
    data["globalRoleId"] = data.pop("global_role_id")
    data["roleName"] = data.pop("name")
    data["roleId"] = data.pop("role_id")
    data["serverName"] = data.pop("server")
    for key, value in data.items():
        if hasattr(current_data, key):
            setattr(current_data, key, value)
    db.save(current_data)
    return prefix + f"[{current_data.roleName} · {current_data.serverName}]"
    
class Player:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def format_jx3api(self) -> dict:
        if self.__dict__ == {}:
            return {"code": 404, "data": None}
        return {"code": 200, "data": self.__dict__}

async def search_player(role_name: str = "", role_id: str = "", server_name: str = "") -> Player:
    player_data = db.where_one(RoleData(), "(roleName = ? OR roleId = ?) AND serverName = ?", role_name, role_id, server_name, default=None)
    if player_data is None:
        uid = await get_uid(roleName=role_name, serverName=server_name)
        if uid is None:
            return Player()
        await get_uid_data(uid, server_name)
        return await search_player(role_name=role_name, role_id=uid)
    else:
        return Player(**player_data.dump())