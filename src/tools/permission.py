import json
from src.tools.utils import *
from src.tools.dep.bot.path import *
from pathlib import Path


def judge(qqnumber):
    file = open(TOOLS+"/permission.json", mode="r")
    json_ = json.loads(file.read())
    file.close()
    if qqnumber not in json_:
        return False
    else:
        return True


def checker(qqnumber: str, score: int) -> bool:
    x = permission_judge(qqnumber, score)
    return x[0]

@ext.use_log()
def permission_judge(qqnumber: str, score: int, action: str = '该操作') -> tuple[bool, int, str]:
    file = open(TOOLS+"/permission.json", mode="r")
    json_ = json.loads(file.read())
    file.close()
    if not isinstance(qqnumber, str):
        qqnumber = str(qqnumber)
    if not isinstance(score, int):
        score = int(score)
    prefix = f'唔……{action}需要授权,但你'
    if qqnumber not in json_:
        return (False, None, f'{prefix}没有任何授权哦~')
    u_level = int(json_[qqnumber])
    if u_level < score:
        return (False, u_level, f'{prefix}的权限只有{u_level}级，要求{score}级~')
    return (True, u_level, None)


def error(score):
    return f"唔……你权限不够哦，这条命令要至少{score}的权限哦~"


def block(sb: str) -> bool:
    with open(TOOLS+"/ban.json", mode="r") as cache:
        for i in json.loads(cache.read()):
            if i == sb:
                return True
        return False
