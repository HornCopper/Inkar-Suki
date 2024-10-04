from typing import Dict, Any

from src.utils.database.classes import Account
from src.utils.database import db

def check_permission(user_id: str | int, level: str | int) -> bool:
    """
    检查用户是否满足某个权限等级。

    Args:
        user_id (str, int): 用户`uin`。
        level (str, int): 至少需达到的权限等级。
    """
    data: Account | Any = db.where_one(Account(), "user_id = ?", int(user_id), default=Account())
    return data.permission >= int(level)

def denied(level: int | str) -> str:
    """
    构造权限不足提示。

    Args:
        level (str, int): 没有达到的权限等级。
    """
    return f"唔……你权限不够哦，这条命令要至少{level}的权限哦~"