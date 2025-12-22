from typing import Any, cast
from nonebot.adapters.onebot.v11 import Bot

from src.utils.time import Time
from src.utils.database import db
from src.utils.database.classes import RandomAffectionRecord

import random

async def get_random_affection(bot: Bot, group_id: int, user_id: int) -> int:
    group_member_list = await bot.get_group_member_list(group_id=group_id)
    group_member_list = [m for m in group_member_list if m["user_id"] != user_id]
    random_group_member = random.choice(group_member_list)
    return random_group_member["user_id"]

def get_affection(user_id: int):
    current_record: RandomAffectionRecord | Any = db.where_one(RandomAffectionRecord(), "user_id = ?", str(user_id), default=None)
    if current_record is None:
        return False
    current_record = cast(RandomAffectionRecord, current_record)
    if Time(current_record.timestamp).is_today:
        return True
    else:
        return False

def set_affection(user_id: int, group_id: int, target_id: int) -> bool:
    current_record: RandomAffectionRecord | Any = db.where_one(RandomAffectionRecord(), "user_id = ?", str(user_id), default=None)
    if current_record is None:
        current_record = RandomAffectionRecord(
            user_id = user_id,
            group_id = group_id,
            target_id = target_id,
            timestamp = Time().raw_time
        )
    else:
        current_record = cast(RandomAffectionRecord, current_record)
        if Time(current_record.timestamp).is_today:
            return False
        current_record.group_id = group_id
        current_record.target_id = target_id
        current_record.timestamp = Time().raw_time
    db.save(current_record)
    return True