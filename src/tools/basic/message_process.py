from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Bot, Event
from nonebot.adapters import Bot
from nonebot.exception import MockApiException
from nonebot.log import logger

import os
import json
import re
import httpx
import random

from ..basic import DATA, write, Config, get_api, read

def getGroupData(group: str, key: str):
    data = json.loads(read(DATA + "/" + str(group) + "/jx3group.json"))
    if data == False:
        return False
    return data[key]

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

async def post_url(url: str, headers: dict = {}, data: dict = {}):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.post(url, headers=headers, data=data)
        json_ = resp.json()
        return json_

@Bot.on_calling_api
async def handle_api_call(bot: Bot, api: str, data: dict):
    if api in ["send_group_msg", "send_private_msg", "send_msg"]:
        if "whitelist" in list(data):
            data.pop("whitelist")
            return
        message = re.sub(r"\[.*?\]", "", str(data["message"]))
        logger.info(message)
        if message == "":
            return
        to_check_headers = {
            "word": message
        }
        data = await post_url("https://inkar-suki.codethink.cn/banword", data=to_check_headers)
        data = data["code"]
        if data == 200:
            raise MockApiException("The message includes banned word!")

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
    group_cfg = getGroupData(str(event.group_id), "subscribe")
    if ans == status and "骚话" in group_cfg:
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