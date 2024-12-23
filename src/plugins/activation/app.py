from typing import Any
from nonebot import get_bots

from src.utils.database import db
from src.utils.database.classes import GroupSettings
from src.utils.nonebot_plugins import scheduler
from src.utils.time import Time

def get_expire_at(group_id: int) -> str:
    group_setting: GroupSettings | Any | None = db.where_one(GroupSettings(), "group_id = ?", str(group_id))
    if group_setting is None or group_setting.expire == 0:
        return "尚未授权， 可输入“授权 天数”进行授权！"
    if group_setting.expire == -1:
        return "授权正常！\n授权到期：N/A"
    if group_setting.expire < Time().raw_time:
        return "授权已过期，请使用“授权 天数”进行授权！\n授权到期：" + Time(group_setting.expire).format()
    else:
        return "授权正常！\n授权到期：" + Time(group_setting.expire).format()

def update_expire_time(group_id: int, days: int) -> str:
    if days > 30:
        return "授权一次最多可以提升30天！"
    elif days == -1:
        group_setting: GroupSettings | Any | None = db.where_one(GroupSettings(), "group_id = ?", str(group_id))
        if group_setting is None:
            group_setting = GroupSettings(group_id = str(group_id), expire=-1)
        else:
            group_setting.expire = -1
        db.save(group_setting)
        return "已更新授权时间！\n授权到期：永久"
    else:
        new_expire = Time().raw_time + days*24*60*60
        group_setting: GroupSettings | Any | None = db.where_one(GroupSettings(), "group_id = ?", str(group_id))
        if group_setting is None:
            group_setting = GroupSettings(group_id = str(group_id), expire=new_expire)
        else:
            group_setting.expire = new_expire
        db.save(group_setting)
        return "已更新授权时间！\n授权到期：" + Time(new_expire).format()

# @scheduler.scheduled_job("cron", hour="7", minute="00")
# async def check_activation():
#     bots = get_bots()
#     database: list[GroupSettings] | Any = db.where_all(GroupSettings(), default=[])

#     for bot in bots.values():
#         account_groups: list[str] = [
#             str(g["group_id"])
#             for g
#             in (await bot.call_api("get_group_list"))
#         ]
#         database_groups: list[GroupSettings] = [
#             g
#             for g
#             in database
#             if g.group_id
#             in account_groups
#         ]
#         for group in database_groups:
#             if group.expire == 0:
#                 group.expire = Time().raw_time + 24*60*60
#             elif group.expire == -1:
#                 continue
#             else:
#                 if Time().raw_time > group.expire:
#                     await bot.call_api("set_group_leave", group_id=int(group.group_id))