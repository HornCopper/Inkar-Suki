from typing import Optional, Union, Any

from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Bot, MessageEvent
from nonebot.adapters import Bot
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor, run_postprocessor
from nonebot.params import RawCommand

from .group_opeator import getGroupSettings
from ..data import group_db, Population, BannedWordList
from ..config import Config
from ..utils import get_api

import re
import random

@run_postprocessor
async def _(bot: Bot, event: MessageEvent, exception: Optional[Exception], cmd = RawCommand()):
    if cmd == None:
        return
    if exception:
        if isinstance(event, GroupMessageEvent):
            await bot.call_api("send_group_msg", group_id=event.group_id, message=f"呜……音卡处理消息中遇到了代码错误，请将本消息告知开发者！\n{exception.__class__}: {exception}\n原始命令：\n{event.raw_message}\n特别提示：如果是属性报错，可以尝试使用属性v1或者属性v4！")
        if isinstance(event, PrivateMessageEvent):
            await bot.call_api("send_private_msg", user_id=event.user_id, message=f"呜……音卡处理消息中遇到了代码错误，请将本消息告知开发者！\n{exception.__class__}: {exception}\n原始命令：\n{event.raw_message}")

@run_preprocessor
async def _(cmd = RawCommand()):
    if cmd == None:
        return
    current_data: Union[Population, Any] = group_db.where_one(Population(), default=Population())
    current_populations = current_data.populations
    if cmd not in current_populations:
        current_populations[cmd] = 1
    else:
        current_populations[cmd] += 1
    current_data.populations = current_populations
    group_db.save(current_data)

preprocess = on_message(priority=0, block=False)

@Bot.on_calling_api
async def _(bot: Bot, api: str, data: dict):
    if api in ["send_group_msg", "send_private_msg", "send_msg"]:
        message = re.sub(r"\[.*?\]", "", str(data["message"]))
        if message == "":
            return
        if "whitelist" in list(data):
            data.pop("whitelist")
            return
        banword_data: Union[BannedWordList, Any] = group_db.where_one(BannedWordList(), default=BannedWordList())
        banword_list = banword_data.banned_word_list
        for i in banword_list:
            if message.find(i) != -1:
                data["message"] = "唔……音卡本来想给告诉你的，可是检测到了不好的内容，所以只能隐藏啦，不然音卡的小鱼干会被没收的T_T"


@preprocess.handle()
async def _(event: MessageEvent, matcher: Matcher):
    msg = str(event.message)
    banword_data: Union[BannedWordList, Any] = group_db.where_one(BannedWordList(), default=BannedWordList())
    for i in banword_data.banned_word_list:
        if msg.find(i) != -1:
            matcher.stop_propagation()

@preprocess.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    group_id = str(event.group_id)
    message = str(event.message)
    group_subscribes = getGroupSettings(str(event.group_id), "subscribe")
    group_addtions = getGroupSettings(group_id, "addtions")
    if not isinstance(group_addtions, list) or not isinstance(group_subscribes, list):
        return
    if ("禁言" in group_addtions) and ("订阅" not in message and "退订" not in message):
        matcher.stop_propagation()
    if "骚话" in group_subscribes:
        chance = random.randint(1, 100)
        if chance % 25 == 0:
            sh_d = await get_api(f"{Config.jx3.api.url}/data/saohua/random")
            sh = sh_d["data"]["text"]
            await bot.call_api("send_group_msg", group_id=event.group_id, message=sh)

@preprocess.handle()
async def _(event: PrivateMessageEvent):
    if str(event.user_id) in list(Config.bot_basic.bot_notice.__dict__):
        return
    await preprocess.finish("呜喵？如果你想要音卡去你的群聊一起玩的话，请前往我们的用户群找我哦，群号为：650495414\n另附：如果正在寻找文档，请点击下方链接前往：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/\n如果愿意给音卡赞助，还可以点击下面的链接支持音卡：\nhttps://inkar-suki.codethink.cn/Inkar-Suki-Docs/#/donate")