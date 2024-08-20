from typing import Union

from src.tools.config import Config
from src.tools.utils.request import post_url
from src.tools.basic.jx3 import gen_ts, gen_xsk, format_body
from src.tools.basic.data_server import server_mapping, Zone_mapping
from src.tools.data import group_db, RoleData

try:
    from .uid import get_uid
    # 如果有能够获取UID的方法，请在这里提供
except:
    pass

import json

ticket = Config.jx3.api.ticket

async def getRoleData(role_id: str = "", server: str = None, group_id: str = None):
    server: Union[str, None] = server_mapping(server, group_id)
    if server is None:
        return ["唔……本群尚未绑定服务器，请绑定后重试！"]
    else:
        current_data: RoleData = group_db.where_one(RoleData(), "roleId = ?", role_id, default=RoleData())
        if current_data.roleName != "":
            prefix = f"绑定成功！\n覆盖数据：[{current_data.roleName} · {current_data.serverName}] -> "
        else:
            prefix = f"绑定成功！\n记录数据："
        param = {
            "role_id": role_id,
            "zone": Zone_mapping(server),
            "server": server,
            "ts": gen_ts()
        }
        param = format_body(param)
        headers = {
            "Host": "m.pvp.xoyo.com",
            "accept": "application/json",
            "deviceid": ticket.split("::")[-1],
            "platform": "ios",
            "gamename": "jx3",
            "clientkey": "1",
            "cache-control": "no-cache",
            "apiversion": "1",
            "sign": "true",
            "token": ticket,
            "Content-Type": "application/json",
            "Connection": "Keep-Alive",
            "User-Agent": "SeasunGame/178 CFNetwork/1240.0.2 Darwin/20.5.0",
            "X-Sk": gen_xsk(param)
        }
        data = await post_url("https://m.pvp.xoyo.com/role/indicator", data=param, headers=headers)
        data = json.loads(data)
        data = data["data"]["role_info"]
        if data == None:
            return f"未找到该玩家，请检查UID后重试！"
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
        group_db.save(current_data)
        return prefix + f"[{current_data.roleName} · {current_data.serverName}]"
    
class Player:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def format_jx3api(self):
        if self.__dict__ == {}:
            return {"code": 404, "data": None}
        return {"code": 200, "data": self.__dict__}
    
from src.tools.utils.request import get_api

async def get_player_local_data(role_name: str = "", role_id: str = "", server_name: str = None):
    player_data = group_db.where_one(RoleData(), "roleName = ? OR roleId = ? AND serverName = ?", role_name, role_id, server_name, default=None)
    if player_data is None:
        uid = await get_uid(roleName=role_name, serverName=server_name)
        if uid == None:
            return Player()
        await getRoleData(uid, server_name)
        return await get_player_local_data(role_name=role_name, role_id=uid)
    else:
        return Player(**player_data.dump())