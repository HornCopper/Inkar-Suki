from typing import Union, Any
from nonebot import get_bots

import os
import pathlib2

from ..data import group_db, GroupSettings

tools_path = f"{os.getcwd()}/src/tools"

def get_path(path: str) -> str:
    t = pathlib2.Path(tools_path)
    return t.parent.joinpath(path).__str__()

DATA = get_path("data")

def getGroupSettings(group_id: str, key: str = None) -> Union[Any, bool]:
    group_data: Union[GroupSettings, None] = group_db.where_one(GroupSettings(), "group_id = ?", group_id, default=None)
    if group_data is not None:
        return group_data.dump().get(key) if key else group_data.dump()
    else:
        group_db.save(GroupSettings(group_id=group_id))
        return getattr(GroupSettings(), key)

def setGroupSettings(group_id: str, key: str, content: Any) -> bool:
    group_data: Union[GroupSettings, None] = group_db.where_one(GroupSettings(), "group_id = ?", group_id, default=None)
    if group_data is None:
        group_data = GroupSettings(group_id=group_id)
    else:
        group_db.delete(GroupSettings(), "group_id = ?", group_id, allow_empty=False)
    if key not in group_data.__dict__:
        raise KeyError("Unknown key of class `group_data`.")
    setattr(group_data, key, content)
    group_db.save(group_data)

def getAllGroups():
    all_db_obj = group_db.where_all(GroupSettings())
    groups = []
    for group_settings in all_db_obj:
        groups.append(group_settings.group_id)
    return groups

async def send_subscribe(subscribe, msg, server=None):
    bots = get_bots()
    groups = getAllGroups()
    group = {}

    for i in list(bots):
        single_groups = await bots[i].call_api("get_group_list")
        group_id_s = []
        for x in single_groups:
            group_id_s.append(x["group_id"])
        group[i] = group_id_s
    
    for group_id in groups:
        for x in list(group):
            if int(group_id) in group[x]:
                if subscribe in getGroupSettings(str(group_id), "subscribe"):
                    group_server = getGroupSettings(str(group_id), "server")
                    if server is not None and (group_server == "" or group_server != server):
                        continue
                    await bots[x].call_api("send_group_msg", group_id=int(group_id), message=msg)