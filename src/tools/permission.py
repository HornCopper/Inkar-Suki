import json
from pathlib import Path
import nonebot
TOOLS = nonebot.get_driver().config.tools_path


def judge(qqnumber):
    file = open(TOOLS+"/permission.json", mode="r")
    json_ = json.loads(file.read())
    file.close()
    if qqnumber not in json_:
        return False
    else:
        return True


def checker(qqnumber: str, score: int):
    file = open(TOOLS+"/permission.json", mode="r")
    json_ = json.loads(file.read())
    file.close()
    if qqnumber not in json_:
        return False
    else:
        if (int(json_[qqnumber]) >= score) == False:
            return False
        else:
            return True


def error(score):
    return f"唔……你权限不够哦，这条命令要至少{score}的权限哦~"

def block(sb: str) -> bool:
    with open(TOOLS+"/ban.json", mode="r") as cache:
        for i in json.loads(cache.read()):
            if i == sb:
                return True
        return False
