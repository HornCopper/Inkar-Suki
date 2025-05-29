from typing import Any

from src.config import Config
from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.network import Request
from src.utils.database import db
from src.utils.database.classes import RoleData

import re
import json

async def get_uid(roleName: str, serverName: str):
    if Config.jx3.api.enable:
        try:
            data = (await Request(f"{Config.jx3.api.url}/data/role/detailed?token={Config.jx3.api.token}&server={serverName}&name={roleName}").get()).json()
        except json.decoder.JSONDecodeError:
            return None
        if data["code"] != 200:
            return None
        return data["data"]["roleId"]
    else:
        return None

async def get_uid_data(role_id: str = "", server: str = "", role_name: str = "") -> str:
    current_data: RoleData | Any = db.where_one(RoleData(), "roleId = ? AND serverName = ?", role_id, server, default=RoleData())
    if current_data.roleName != "":
        prefix = f"绑定成功！\n覆盖数据：[{current_data.roleName} · {current_data.serverName}] -> "
    else:
        prefix = "绑定成功！\n记录数据："
    params = {
        "role_id": role_id,
        "zone": Server(server).zone,
        "server": server
    }
    data = (await Request("https://m.pvp.xoyo.com/role/indicator", params=params).post(tuilan=True)).json()
    data: dict[str, Any] = data["data"]["role_info"]
    if data is None:
        return PROMPT.UIDInvalid
    data["bodyName"] = data.pop("body_type")
    data["campName"] = data.pop("camp")
    data["forceName"] = data.pop("force")

    _global_role_id = data.pop("global_role_id")
    db.delete(RoleData(), "globalRoleId = ?", _global_role_id)
    data["globalRoleId"] = _global_role_id

    _role_name = data.pop("name")
    data["roleName"] = _role_name if "*" not in _role_name else role_name
    db.delete(RoleData(), "roleName = ? AND serverName = ?", data["roleName"], server)

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
    
    def format_jx3api(self) -> dict[str, Any]:
        if self.__dict__ == {}:
            return {"code": 404, "data": None}
        if self.__dict__["serverName"] not in Server.server_aliases.keys():
            return {"code": 404, "data": None}
        return {"code": 200, "data": self.__dict__}

async def search_player(
    role_name: str = "",
    role_id: str = "",
    server_name: str = "",
    *,
    local_lookup: bool = False
) -> Player:
    if "·" in role_name:
        role_name, server_name = role_name.split("·")
        role_name = role_name.lstrip("[")
        server_name = server_name.rstrip("]")
    if not bool(re.match(r"^[\u4e00-\u9fff0-9@]*$", role_name)):
        return Player()
    player_data = db.where_one(RoleData(), "(roleName = ? OR roleId = ?) AND serverName = ?", role_name, role_id, server_name, default=None)
    if player_data is None and not local_lookup:
        uid = await get_uid(roleName=role_name, serverName=server_name)
        if uid is None:
            return Player()
        await get_uid_data(uid, server_name, role_name)
        player_data = db.where_one(RoleData(), "(roleName = ? OR roleId = ?) AND serverName = ?", role_name, role_id, server_name, default=None)
        if player_data is None:
            return Player()
        else:
            return Player(**player_data.dump())
    elif player_data is not None:
        return Player(**player_data.dump())
    else:
        return Player()