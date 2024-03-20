from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Bot

import os
import json
import random

from ..basic import DATA, write, Config, get_api

preprocess = on_message(priority=0, block=False)

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
async def checkEnv(bot: Bot, event: GroupMessageEvent):
    group_id = str(event.group_id)
    files = {
        "blacklist.json": [],
        "jx3group.json": {"server": "", "group": group_id, "subscribe": [], "welcome": "欢迎入群！"},
        "webhook.json": [],
        "opening.json": [],
        "wiki.json": {"startwiki":"","interwiki":[]},
        "record.json": []
    }
    status = []
    for i in list(files):
        if os.path.exists(DATA + "/" + group_id + "/" + i):
            status.append(True)
            continue
        status.append(False)
        write(DATA + "/" + group_id + "/" + i, json.dumps(files[i]))
    ans = []
    for i in range(len(list(files))):
        ans.append(True)
    if ans == status:
        chance = random.randint(1, 100)
        if chance % 25 == 0:
            sh_d = await get_api("https://www.jx3api.com/data/saohua/random")
            sh = sh_d["data"]["text"]
            await bot.call_api("send_group_msg", group_id=event.group_id, message=sh)
            

@preprocess.handle()
async def autoPrivate(event: PrivateMessageEvent):
    if str(event.user_id) in Config.bot:
        return
    await preprocess.finish("呜喵？如果你想要音卡去你的群聊一起玩的话，请前往我们的用户群找我哦，群号为：650495414\n另附：如果正在寻找文档，请点击下方链接前往：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/\n如果愿意给音卡赞助，还可以点击下面的链接支持音卡：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/donate")
