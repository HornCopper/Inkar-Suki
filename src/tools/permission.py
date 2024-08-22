import json

from src.tools.data import group_db, Permission

def get_all_admin():
    data: Permission = group_db.where_one(Permission(), default=Permission())
    return data

def judge(user_id: str) -> bool:
    data = get_all_admin().permissions_list
    return user_id in data

def checker(user_id: str, level: int):
    data = get_all_admin()
    data = data.permissions_list
    return False if user_id not in data else int(data[user_id]) >= level

def error(level):
    return f"唔……你权限不够哦，这条命令要至少{level}的权限哦~"

def block(user_id: str) -> bool:
    data = get_all_admin()
    data = data.permissions_list
    for i in json.loads(data):
        if i == user_id:
            return True
    return False