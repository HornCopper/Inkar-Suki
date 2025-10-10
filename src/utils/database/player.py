from typing import Any, Literal, overload

from src.config import Config
from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.network import Request
from src.utils.database import db
from src.utils.database.classes import RoleData

import re
import json

async def get_role_id(roleName: str, serverName: str) -> dict | None:
    if Config.jx3.api.enable:
        response = await Request(f"{Config.jx3.api.url}/data/role/detailed?token={Config.jx3.api.token}&server={serverName}&name={roleName}").get()
        if response.status_code != 200:
            return None
        data = response.json()
        if data["code"] != 200:
            return None
        return data["data"]
    else:
        return None
    
@overload
async def get_uid_data(global_role_id: str = "", role_id: str = "", server: str = "", role_name: str = "", msg: Literal[True] = True) -> str: ...

@overload
async def get_uid_data(global_role_id: str = "", role_id: str = "", server: str = "", role_name: str = "", msg: Literal[False] = False) -> RoleData: ...

async def get_uid_data(global_role_id: str = "", role_id: str = "", server: str = "", role_name: str = "", msg: bool = True) -> str | RoleData:
    current_data: RoleData | None | Any = db.where_one(RoleData(), "roleId = ? AND serverName = ?", role_id, server, default=None)
    if current_data is not None:
        prefix = f"绑定成功！\n原始数据：[{current_data.roleName} · {current_data.serverName}]\n更新数据："
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
        return PROMPT.UIDInvalid if msg else RoleData()
    bodyName = data.pop("body_type")
    campName = data.pop("camp")
    forceName = data.pop("force")

    _global_role_id = global_role_id
    db.delete(RoleData(), "globalRoleId = ?", _global_role_id)
    globalRoleId = _global_role_id

    _role_name = data.pop("name")
    roleName = _role_name if "*" not in _role_name else role_name

    if not global_role_id and role_id:
        resp = await Request(f"{Config.jx3.api.url}/data/role/detailed?token={Config.jx3.api.token}&server={server}&name={roleName}").get()
        api_data = resp.json()
        if api_data["code"] == 200:
            globalRoleId = api_data["data"]["globalRoleId"]

    db.delete(RoleData(), "roleName = ? AND serverName = ?", roleName, server)

    roleId = data.pop("role_id")
    serverName = data.pop("server")
    
    updated_data = RoleData(
        bodyName=bodyName,
        campName=campName,
        forceName=forceName,
        globalRoleId=globalRoleId,
        roleName=roleName,
        roleId=roleId,
        serverName=serverName
    )

    db.save(updated_data)

    if msg:
        return prefix + f"[{roleName} · {serverName}]"
    else:
        return updated_data

async def search_player(
    role_name: str = "",
    role_id: str = "",
    server_name: str = "",
    *,
    local_lookup: bool = False
) -> RoleData:
    if "·" in role_name:
        role_name, server_name = role_name.split("·")
        role_name = role_name.lstrip("[")
        server_name = server_name.rstrip("]")
    if not bool(re.match(r"^[\u4e00-\u9fff0-9@]*$", role_name)):
        return RoleData()
    player_data: RoleData | Any = db.where_one(RoleData(), "(roleName = ? OR roleId = ?) AND serverName = ?", role_name, role_id, server_name, default=RoleData())
    if player_data.roleId == "" and not local_lookup:
        uid_data = await get_role_id(roleName=role_name, serverName=server_name)
        if uid_data is None:
            return RoleData()
        player_data = await get_uid_data(uid_data["globalRoleId"], uid_data["roleId"], server_name, role_name, False)
        return player_data
    else:
        return player_data