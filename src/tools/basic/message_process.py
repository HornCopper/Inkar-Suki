from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Bot, Event
from nonebot.adapters import Bot
from nonebot.exception import MockApiException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import RawCommand

import os
import json
import re
import random

from ..basic import DATA, write, Config, get_api, read, TOOLS

from .spark import chat_spark

@run_preprocessor
async def _(cmd = RawCommand()):
    if cmd == None:
        return
    current_data = json.loads(read(TOOLS + "/population.json"))
    if cmd not in current_data:
        current_data[cmd] = 1
    else:
        current_data[cmd] += 1
    write(TOOLS + "/population.json", json.dumps(current_data, ensure_ascii=False))
    
    

def getGroupData(group: str, key: str):
    data = read(DATA + "/" + str(group) + "/settings.json")
    if not data:
        return False
    else:
        data = json.loads(data)
    return data[key]

preprocess = on_message(priority=0, block=False)

"""
new_path = f"{DATA}/{str(group_id)}"
if os.path.exists(f"{new_path}/blacklist.json"):
    return True
os.mkdir(new_path)
write(f"{new_path }/settings.json", "{\"group\":\"" + str(group_id) +
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

@Bot.on_calling_api
async def _(bot: Bot, api: str, data: dict):
    if api in ["send_group_msg", "send_private_msg", "send_msg"]:
        message = re.sub(r"\[.*?\]", "", str(data["message"]))
        if message == "":
            return
        if "whitelist" in list(data):
            data.pop("whitelist")
            return
        banword = json.loads(read(TOOLS + "/banword.json"))
        for i in banword:
            if message.find(i) != -1:
                data["message"] = "唔……音卡本来想给告诉你的，可是检测到了不好的内容，所以只能隐藏啦，不然音卡的小鱼干会被没收的T_T"


@preprocess.handle()
async def _(event: Event, matcher: Matcher):
    msg = str(event.message)
    banword = json.loads(read(TOOLS + "/banword.json"))
    for i in banword:
        if msg.find(i) != -1:
            matcher.stop_propagation()

@preprocess.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    group_id = str(event.group_id)
    message = str(event.message)
    files = {
        "blacklist.json": [],
        "settings.json": {"server": "", "group": group_id, "subscribe": [], "addtions": [], "welcome": "欢迎入群！"},
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
    group_cfg = getGroupData(str(event.group_id), "subscribe")
    if "禁言" in getGroupData(group_id, "addtions") and ("订阅" not in message and "退订" not in message):
        matcher.stop_propagation()
    if ans == status and "骚话" in group_cfg:
        chance = random.randint(1, 100)
        if chance % 25 == 0:
            sh_d = await get_api("https://www.jx3api.com/data/saohua/random")
            sh = sh_d["data"]["text"]
            await bot.call_api("send_group_msg", group_id=event.group_id, message=sh)

@preprocess.handle()
async def _(event: PrivateMessageEvent):
    if str(event.user_id) in Config.bot:
        return
    await preprocess.finish("呜喵？如果你想要音卡去你的群聊一起玩的话，请前往我们的用户群找我哦，群号为：650495414\n另附：如果正在寻找文档，请点击下方链接前往：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/\n如果愿意给音卡赞助，还可以点击下面的链接支持音卡：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/donate")