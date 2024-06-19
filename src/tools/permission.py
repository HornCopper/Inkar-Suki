import json
import pathlib2
import os

tools_path = f"{os.getcwd()}/src/tools"

def get_path(path: str) -> str:
    t = pathlib2.Path(tools_path)
    return t.parent.joinpath(path).__str__()

TOOLS = get_path("tools")

def judge(qqnumber):
    with open(TOOLS + "/permission.json", mode="r") as file:
        json_ = json.loads(file.read())
    return qqnumber in json_

def checker(qqnumber: str, score: int):
    with open(TOOLS + "/permission.json", mode="r") as file:
        json_ = json.loads(file.read())
    return False if qqnumber not in json_ else int(json_[qqnumber]) >= score


def error(score):
    return f"唔……你权限不够哦，这条命令要至少{score}的权限哦~"


def block(sb: str) -> bool:
    with open(TOOLS + "/ban.json", mode="r") as cache:
        for i in json.loads(cache.read()):
            if i == sb:
                return True
        return False