from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment as ms

from src.const.path import ASSETS, build_path
from src.utils.file import read
from src.utils.database.operation import set_group_settings, get_group_settings

from .about import generate_group_info

import json

EnableMatcher = on_command("jx3_subscribe", aliases={"订阅", "开启"}, force_whitespace=True, priority=5)

@EnableMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) == 0:
        await EnableMatcher.finish("唔……开启失败，您似乎没有告诉我您要订阅的内容？")
    else:
        subscribe_options = json.loads(read(build_path(ASSETS, ["source", "subscribe"], end_with_slash=True) + "options.json"))
        addition_options = json.loads(read(build_path(ASSETS, ["source", "subscribe"], end_with_slash=True) + "additions.json"))
        if not set(arg).issubset(set(list(subscribe_options) + list(addition_options))):
            await EnableMatcher.finish("唔……开启失败，虽然音卡可以一次开启多个订阅，但是好像您这里包含了不应该存在的订阅内容，请检查后重试！\n可使用“关于”查看可订阅的内容！")
        current_subscribes = get_group_settings(str(event.group_id), "subscribe")
        current_additions = get_group_settings(str(event.group_id), "additions")
        if not isinstance(current_additions, list) or not isinstance(current_subscribes, list):
            return
        for i in arg:
            if i in current_subscribes or i in current_additions:
                continue
            if i in subscribe_options:
                current_subscribes.append(i)
            elif i in addition_options:
                current_additions.append(i)
        set_group_settings(str(event.group_id), "subscribe", current_subscribes)
        set_group_settings(str(event.group_id), "additions", current_additions)
        await EnableMatcher.finish("订阅成功！\n可使用“关于”查看本群详细信息！")

DisableMatcher = on_command("jx3_unsubscribe", aliases={"退订", "关闭"}, force_whitespace=True, priority=5)

@DisableMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) == 0:
        await DisableMatcher.finish("唔……关闭失败，您似乎没有告诉我您要退订的内容？")
    else:
        subscribe_options = json.loads(read(build_path(ASSETS, ["source", "subscribe"], end_with_slash=True) + "options.json"))
        addition_options = json.loads(read(build_path(ASSETS, ["source", "subscribe"], end_with_slash=True) + "additions.json"))
        if not set(arg).issubset(set(list(subscribe_options) + list(addition_options))):
            await EnableMatcher.finish("唔……关闭失败，虽然音卡可以一次关闭多个订阅，但是好像您这里包含了不应该存在的退订内容，请检查后重试！\n可使用“关于”查看可订阅的内容！")
        currentSubscribe = get_group_settings(str(event.group_id), "subscribe")
        currentAddition = get_group_settings(str(event.group_id), "additions")
        if not isinstance(currentAddition, list) or not isinstance(currentSubscribe, list):
            return
        for i in arg:
            if i not in currentSubscribe and i not in currentAddition:
                continue
            if i in currentSubscribe:
                currentSubscribe.remove(i)
            elif i in currentAddition:
                currentAddition.remove(i)
        set_group_settings(str(event.group_id), "subscribe", currentSubscribe)
        set_group_settings(str(event.group_id), "additions", currentAddition)
        await DisableMatcher.finish("退订成功！\n可使用“关于”查看本群详细信息！")

info = on_command("jx3_about", aliases={"关于", "本群订阅"}, force_whitespace=True, priority=5)

@info.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    about_img = await generate_group_info(bot, str(event.group_id))
    if not isinstance(about_img, str):
        return
    await info.finish(ms.image(about_img))