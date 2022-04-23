import json
import os
def judge(qqnumber):
    file = open("/root/nb/src/tools/permission.json", mode = "r")
    file.close()
    json_ = json.loads(file.read())
    if qqnumber not in json_:
        return False
    else:
        return True
def checker(qqnumber:str,score:int):
    file = open("/root/nb/src/tools/permission.json", mode = "r")
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
    with open("/root/nb/src/tools/ban.json",mode="r") as cache:
        for i in json.loads(cache.read()):
            if i == sb:
                return True
        return False