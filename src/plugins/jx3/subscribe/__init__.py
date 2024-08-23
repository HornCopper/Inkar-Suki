from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment as ms

from src.tools.utils.file import read
from src.tools.utils.path import PLUGINS
from src.tools.basic.group import getGroupSettings, setGroupSettings

from .about import *

import json

subscribe_enable = on_command("jx3_subscribe", aliases={"订阅", "开启"}, force_whitespace=True, priority=5)

@subscribe_enable.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) == 0:
        await subscribe_enable.finish("唔……开启失败，您似乎没有告诉我您要订阅的内容？")
    else:
        subscribe_options = json.loads(read(PLUGINS + "/jx3/subscribe/options.json"))
        addtion_options = json.loads(read(PLUGINS + "/jx3/subscribe/addtions.json"))
        if not set(arg).issubset(set(list(subscribe_options) + list(addtion_options))):
            await subscribe_enable.finish("唔……开启失败，虽然音卡可以一次开启多个订阅，但是好像您这里包含了不应该存在的订阅内容，请检查后重试！")
        currentSubscribe = getGroupSettings(str(event.group_id), "subscribe")
        currentAddtion = getGroupSettings(str(event.group_id), "addtions")
        if not isinstance(currentAddtion, list) or not isinstance(currentSubscribe, list):
            return
        for i in arg:
            if i in currentSubscribe or i in currentAddtion:
                continue
            if i in subscribe_options:
                currentSubscribe.append(i)
            elif i in addtion_options:
                currentAddtion.append(i)
        setGroupSettings(str(event.group_id), "subscribe", currentSubscribe)
        setGroupSettings(str(event.group_id), "addtions", currentAddtion)
        await subscribe_enable.finish("订阅成功！\n可使用“关于”查看本群详细信息！")

subscribe_disable = on_command("jx3_unsubscribe", aliases={"退订", "关闭"}, force_whitespace=True, priority=5)

@subscribe_disable.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) == 0:
        await subscribe_disable.finish("唔……关闭失败，您似乎没有告诉我您要退订的内容？")
    else:
        subscribe_options = json.loads(read(PLUGINS + "/jx3/subscribe/options.json"))
        addtion_options = json.loads(read(PLUGINS + "/jx3/subscribe/addtions.json"))
        if not set(arg).issubset(set(list(subscribe_options) + list(addtion_options))):
            await subscribe_enable.finish("唔……关闭失败，虽然音卡可以一次关闭多个订阅，但是好像您这里包含了不应该存在的退订内容，请检查后重试！")
        currentSubscribe = getGroupSettings(str(event.group_id), "subscribe")
        currentAddtion = getGroupSettings(str(event.group_id), "addtions")
        if not isinstance(currentAddtion, list) or not isinstance(currentSubscribe, list):
            return
        for i in arg:
            if i not in currentSubscribe and i not in currentAddtion:
                continue
            if i in currentSubscribe:
                currentSubscribe.remove(i)
            elif i in currentAddtion:
                currentAddtion.remove(i)
        setGroupSettings(str(event.group_id), "subscribe", currentSubscribe)
        setGroupSettings(str(event.group_id), "addtions", currentAddtion)
        await subscribe_disable.finish("退订成功！\n可使用“关于”查看本群详细信息！")

info = on_command("jx3_about", aliases={"关于", "本群订阅"}, force_whitespace=True, priority=5)

@info.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    about_img = await generateGroupInfo(bot, str(event.group_id))
    if not isinstance(about_img, str):
        return
    await info.finish(ms.image(about_img))