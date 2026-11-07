from typing import Any, Literal, overload

from nonebot import get_bots
from nonebot.exception import ActionFailed, NetworkError
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.adapters.qq import Bot as QQBot

from src.utils.database.classes import GroupSettings
from src.utils.database import db
from src.utils.identity import resolve_group_id

@overload
def get_group_settings(group_id: int | str, key: Literal["subscribe"]) -> list[str]:
    ...

@overload
def get_group_settings(group_id: int | str, key: Literal["welcome"]) -> str:
    ...

@overload
def get_group_settings(group_id: int | str, key: Literal["server"]) -> str:
    ...

@overload
def get_group_settings(group_id: int | str, key: Literal["opening"]) -> list[dict]:
    ...

@overload
def get_group_settings(group_id: int | str, key: Literal["additions"]) -> list[str]:
    ...

@overload
def get_group_settings(group_id: int | str, key: Literal["blacklist"]) -> list[dict[str, str]]:
    ...

@overload
def get_group_settings(group_id: int | str, key: Literal["wiki"]) -> dict:
    ...

def get_group_settings(group_id: int | str, key: str = "") -> Any:
    group_id = resolve_group_id(group_id)
    group_data: GroupSettings | Any = db.where_one(GroupSettings(), "group_id = ?", str(group_id), default = None)
    if group_data is not None:
        return group_data.dump().get(key) if key else group_data.dump()
    else:
        db.save(GroupSettings(group_id = str(group_id)))
        return getattr(GroupSettings(), key)

def set_group_settings(group_id: int | str, key: str, content: Any) -> None:
    group_id = resolve_group_id(group_id)
    group_data: GroupSettings | Any = db.where_one(GroupSettings(), "group_id = ?", str(group_id), default = None)
    if group_data is None:
        group_data = GroupSettings(group_id = str(group_id))
    else:
        db.delete(GroupSettings(), "group_id = ?", group_id, allow_empty = False)
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

async def send_subscribe(subscribe: str = "", msg: str | Message = "", server: str | None = "") -> None:
    bots: dict = get_bots()
    if bots == {}:
        return
    groups = get_groups()
    if isinstance(groups, bool):
        return
    group: dict[str, list[int]] = {}
    official = [bot for bot in bots.values() if isinstance(bot, QQBot)]

    for i in list(bots):
        if not isinstance(bots[i], Bot):
            continue
        try:
            single_groups = await bots[i].call_api("get_group_list")
        except Exception:
            continue
        group_id_s = []
        for x in single_groups:
            group_id_s.append(x["group_id"])
        group[i] = group_id_s

    # 协议投递留在共用基础设施，公告和定时任务继续使用原来的 send_subscribe。
    if official:
        from src.adapters.qq_official.proactive import send_group_subscription
        from src.utils.identity import get_identity_store

        identities = get_identity_store()
    for group_id in dict.fromkeys(resolve_group_id(value) for value in groups):
        group_data = get_group_settings(group_id, "subscribe")
        if not isinstance(group_data, list) or subscribe not in group_data:
            continue
        group_server = get_group_settings(group_id, "server")
        if server != "" and (group_server == "" or group_server != server):
            continue
        delivered = False
        for x in list(group):
            if group_id in group[x]:
                try:
                    await bots[x].call_api("send_group_msg", group_id = group_id, message = msg)
                    delivered = True
                except (ActionFailed, NetworkError):
                    continue
        if not delivered:
            for bot in official:
                if await send_group_subscription(bot, identities, group_id, subscribe, msg, server):
                    break
