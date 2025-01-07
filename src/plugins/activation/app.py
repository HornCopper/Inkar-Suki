from typing import Any
from collections import defaultdict
from datetime import datetime, timedelta

from src.utils.database import db
from src.utils.database.lib import Database
from src.utils.database.classes import GroupSettings
from src.utils.time import Time

def process_group_settings(db: Database, group_settings_list: list[GroupSettings]):
    group_id_map = defaultdict(list)
    for g in group_settings_list:
        group_id_map[g.group_id].append(g)
    for group_id, groups in group_id_map.items():
        if len(groups) > 1:
            db.delete(GroupSettings(), "group_id = ?", str(group_id))
            db.save(GroupSettings(group_id=str(group_id)))

def is_within_48_hours(timestamp: int) -> bool:
    current_time = datetime.utcnow()
    target_time = datetime.utcfromtimestamp(timestamp)
    diff = target_time - current_time
    return timedelta(0) <= diff <= timedelta(hours=48)

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
    if days > 30 or (days < 0 and days != -1):
        return "授权一次最多可以提升30天且必须为正整数！"
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