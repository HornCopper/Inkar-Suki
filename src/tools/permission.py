import json

from src.tools.data import group_db, Permission

def get_all_admin():
    data: Permission = group_db.where_one(Permission(), default=Permission())
    return data

def judge(qqnumber):
    data = get_all_admin().permissions_list
    return qqnumber in data

def checker(qqnumber: str, score: int):
    data = get_all_admin()
    data = data.permissions_list
    return False if qqnumber not in data else int(data[qqnumber]) >= score

def error(score):
    return f"唔……你权限不够哦，这条命令要至少{score}的权限哦~"

def block(sb: str) -> bool:
    data = get_all_admin()
    data = data.permissions_list
    for i in json.loads(data):
        if i == sb:
            return True
    return False