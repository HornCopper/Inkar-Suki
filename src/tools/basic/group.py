from typing import Union, Any, Optional, List
from nonebot import get_bots

import os
import pathlib2

from src.tools.database import group_db, GroupSettings

tools_path = f"{os.getcwd()}/src/tools"

def get_path(path: str) -> str:
    t = pathlib2.Path(tools_path)
    return t.parent.joinpath(path).__str__()

DATA = get_path("data")

def getGroupSettings(group_id: str, key: str = "") -> Union[Any, bool]:
    group_data: Union[GroupSettings, Any] = group_db.where_one(GroupSettings(), "group_id = ?", group_id, default=None)
    if group_data is not None:
        return group_data.dump().get(key) if key else group_data.dump()
    else:
        group_db.save(GroupSettings(group_id=group_id))
        return getattr(GroupSettings(), key)

def setGroupSettings(group_id: str, key: str, content: Any) -> Optional[bool]:
    group_data: Union[GroupSettings, Any] = group_db.where_one(GroupSettings(), "group_id = ?", group_id, default=None)
    if group_data is None:
        group_data = GroupSettings(group_id=group_id)
    else:
        group_db.delete(GroupSettings(), "group_id = ?", group_id, allow_empty=False)
    if key not in group_data.__dict__:
        raise KeyError("Unknown key of class `group_data`.")
    setattr(group_data, key, content)
    group_db.save(group_data)

def getAllGroups() -> Union[bool, list]:
    all_db_obj: Optional[List[Union[GroupSettings, Any]]] = group_db.where_all(GroupSettings())
    groups = []
    if not isinstance(all_db_obj, list):
        return False
    for group_settings in all_db_obj:
        groups.append(group_settings.group_id)
    return groups

async def send_subscribe(subscribe: str = "", msg: str = "", server: Optional[str] = ""):
    bots: Optional[dict] = get_bots()
    if bots is {}:
        return
    groups = getAllGroups()
    if isinstance(groups, bool):
        return
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
                group_data = getGroupSettings(str(group_id), "subscribe")
                if not isinstance(group_data, list):
                    return
                if subscribe in group_data:
                    group_server = getGroupSettings(str(group_id), "server")
                    if server != "" and (group_server == "" or group_server != server):
                        continue
                    await bots[x].call_api("send_group_msg", group_id=int(group_id), message=msg)