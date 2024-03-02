from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent

import os
import json

from .. import DATA, write

preprocess = on_message(priority=0)

"""
new_path = f"{DATA}/{str(group_id)}"
if os.path.exists(f"{new_path}/blacklist.json"):
    return True
os.mkdir(new_path)
write(f"{new_path }/jx3group.json", "{\"group\":\"" + str(group_id) +
        "\",\"server\":\"\",\"leader\":\"\",\"leaders\":[],\"name\":\"\",\"status\":false}")
write(f"{new_path }/webhook.json", "[]")
write(f"{new_path }/marry.json", "[]")
write(f"{new_path }/banword.json", "[]")
write(f"{new_path }/opening.json", "[]")
write(f"{new_path }/wiki.json", "{\"startwiki\":\"\",\"interwiki\":[]}")
write(f"{new_path }/arcaea.json", "{}")
write(f"{new_path }/record.json", "[]")
write(f"{new_path }/subscribe.json", "[]")
write(f"{new_path }/blacklist.json", "[]")"""

@preprocess.handle()
async def checkEnv(event: GroupMessageEvent):
    group_id = str(event.group_id)
    files = {
        "blacklist.json": [],
        "jx3group.json": {"server": "", "group": group_id, "subscribe": [], "welcome": "欢迎入群！"},
        "webhook.json": [],
        "opening.json": [],
        "wiki.json": {"startwiki":"","interwiki":[]},
        "record.json": []
    }
    for i in list(files):
        if os.path.exists(DATA + "/" + group_id + "/" + i):
            continue
        write(DATA + "/" + group_id + "/" + i, json.dumps(files[i]))
    