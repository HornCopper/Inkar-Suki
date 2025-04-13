from typing import Any, Literal, overload
from nonebot import get_bots
from nonebot.exception import ActionFailed

from src.utils.database.classes import GroupSettings
from src.utils.database import db

@overload
def get_group_settings(group_id: int | str, key: Literal["subscribe"]) -> list[str]: ...

@overload
def get_group_settings(group_id: int | str, key: Literal["welcome"]) -> str: ...

@overload
def get_group_settings(group_id: int | str, key: Literal["server"]) -> str: ...

@overload
def get_group_settings(group_id: int | str, key: Literal["opening"]) -> list[dict]: ...

@overload
def get_group_settings(group_id: int | str, key: Literal["additions"]) -> list[str]: ...

@overload
def get_group_settings(group_id: int | str, key: Literal["blacklist"]) -> list[dict[str, str]]: ...

@overload
def get_group_settings(group_id: int | str, key: Literal["wiki"]) -> dict: ...

def get_group_settings(group_id: int | str, key: str = "") -> Any:
    group_data: GroupSettings | Any = db.where_one(GroupSettings(), "group_id = ?", str(group_id), default=None)
    if group_data is not None:
        return group_data.dump().get(key) if key else group_data.dump()
    else:
        db.save(GroupSettings(group_id=str(group_id)))
        return getattr(GroupSettings(), key)

def set_group_settings(group_id: int | str, key: str, content: Any) -> None:
    group_data: GroupSettings | Any = db.where_one(GroupSettings(), "group_id = ?", str(group_id), default=None)
    if group_data is None:
        group_data = GroupSettings(group_id=str(group_id))
    else:
        db.delete(GroupSettings(), "group_id = ?", group_id, allow_empty=False)
    if key not in group_data.__dict__:
        raise KeyError("Unknown key of class `group_data`.")
    setattr(group_data, key, content)
    db.save(group_data)

def get_groups() -> bool | list:
    all_db_obj: list[GroupSettings | Any] | None = db.where_all(GroupSettings()) or []
    groups = []
    if not isinstance(all_db_obj, list):
        return False
    for group_settings in all_db_obj:
        group_settings: GroupSettings | Any
        groups.append(group_settings.group_id)
    return groups

async def send_subscribe(subscribe: str = "", msg: str = "", server: str | None = "") -> None:
    bots: dict = get_bots()
    if bots == {}:
        return
    groups = get_groups()
    if isinstance(groups, bool):
        return
    group: dict[str, list[str]] = {}

    for i in list(bots):
        single_groups = await bots[i].call_api("get_group_list")
        group_id_s = []
        for x in single_groups:
            group_id_s.append(x["group_id"])
        group[i] = group_id_s
    
    for group_id in groups:
        for x in list(group):
            if int(group_id) in group[x]:
                group_data = get_group_settings(str(group_id), "subscribe")
                if not isinstance(group_data, list):
                    return
                if subscribe in group_data:
                    group_server = get_group_settings(str(group_id), "server")
                    if server != "" and (group_server == "" or group_server != server):
                        continue
                    try:
                        await bots[x].call_api("send_group_msg", group_id=int(group_id), message=msg)
                    except ActionFailed:
                        continue