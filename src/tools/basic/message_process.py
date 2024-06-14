from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Bot, Event
from nonebot.adapters import Bot
from nonebot.exception import MockApiException
from nonebot.log import logger
from nonebot.matcher import Matcher

import os
import json
import re
import random

from ..basic import DATA, write, Config, get_api, read, TOOLS

from .spark import chat_spark

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
async def handle_api_call(bot: Bot, api: str, data: dict):
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

msg = "唔……很抱歉，在本群检测到了一个抄袭机器人（昵称大致满足xxxx的蓉蓉，例如八方支援的蓉蓉），它涉嫌抄袭我们的代码，具体可以参考这篇文章：https://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/notice，本群服务已被暂停，如果还要继续使用音卡，请先移除蓉蓉机器人，随后前往音卡用户群（650495414）再次领养，完全免费！"
msg1 = """
--------
发送[功能]查看所有功能。
发送[领养]领取一只自己的机器人。
发送[蓉蓉下班]让我闭嘴。
发送[移除蓉蓉]让我退群。
--------
如果发现蓉蓉不说话或者有问题了，请到大群沟通。
不要直接踢或禁言，这行为对蓉蓉很危险。QAQ"""
msg2 = "这不是我的同类同胞嘛，你也来啦！一起玩耍吧！"

pattern = r'来自\[(.*?)\]*订阅，回复\[退订 (.*?)\]退订'

@preprocess.handle()
async def checkEnv(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    rec = event.message.extract_plain_text()
    match_rong_sb = re.search(pattern, rec) or rec.find(msg1) != -1 or rec.find(msg2) != -1
    if match_rong_sb:
        await bot.call_api("send_group_msg", group_id=event.group_id, message=msg)
        await bot.call_api("set_group_leave", group_id=event.group_id)
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
async def autoPrivate(event: PrivateMessageEvent):
    if str(event.user_id) in Config.bot:
        return
    await preprocess.finish("呜喵？如果你想要音卡去你的群聊一起玩的话，请前往我们的用户群找我哦，群号为：650495414\n另附：如果正在寻找文档，请点击下方链接前往：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/\n如果愿意给音卡赞助，还可以点击下面的链接支持音卡：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/donate")

@preprocess.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    message = event.message
    if len(message) == 1 and message[0].type == "text":
        if len(event.message.extract_plain_text()) > 30:
            return
        if "随机AI" in getGroupData(str(event.group_id), "subscribe"):
            chance = random.randint(1, 100)
            if chance % 50 == 0:
                rd_resp = await chat_spark(message.extract_plain_text())
                await bot.call_api("send_group_msg", group_id=event.group_id, message=rd_resp)