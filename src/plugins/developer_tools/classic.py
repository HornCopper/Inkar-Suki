from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent
from nonebot.params import CommandArg
from nonebot.adapters import Message

from src.tools.utils.time import convert_time, get_current_time
from src.tools.utils.num import check_number
from src.tools.permission import checker, error
from src.tools.utils.path import CACHE
from src.tools.basic.group import getAllGroups
from src.tools.config import Config

import os
import random

purge = on_command("purge", force_whitespace=True, priority=5)  # 清除所有`help`生成的缓存图片


@purge.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    if not checker(str(event.user_id), 10):
        await purge.finish(error(10))
    try:
        for i in os.listdir(CACHE):
            os.remove(CACHE + "/" + i)
    except Exception as _:
        await purge.finish("部分文件并没有找到哦~")
    else:
        await purge.finish("好的，已帮你清除图片缓存~")

echo = on_command("echo", force_whitespace=True, priority=5)  # 复读只因功能

@echo.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await echo.finish(error(10))
    await echo.finish(args)

ping = on_command("ping", force_whitespace=True, priority=5)  # 测试机器人是否在线

@ping.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    permission = checker(str(event.user_id), 1)
    if not permission:
        await ping.finish(f"咕咕咕，音卡来啦！\n当前时间为：{convert_time(get_current_time())}\n欢迎使用Inkar-Suki！")
    else:
        groups = await bot.call_api("get_group_list")
        group_count = len(groups)
        friends = await bot.call_api("get_friend_list")
        friend_count = len(friends)
        registers = getAllGroups()
        if not isinstance(registers, list):
            return
        register_count = len(registers)
        msg = f"咕咕咕，音卡来啦！\n现在是：{convert_time(get_current_time())}\n{group_count} | {register_count} | {friend_count}\n您拥有机器人的管理员权限！"
    await ping.finish(msg)

post = on_command("post", force_whitespace=True, priority=5)  # 发送全域公告至每一个机器人加入的QQ群。


@post.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if str(event.user_id) not in Config.bot_basic.bot_owner:
        await post.finish("唔……只有机器人主人可以使用该命令哦~")
    cmd = args.extract_plain_text()
    groups = await bot.call_api("get_group_list")
    for i in groups:
        await bot.call_api("send_group_msg",
                           group_id=i["group_id"],
                           message=cmd
                           )

git = on_command("-git", force_whitespace=True, priority=5)  # 调用`Git`，~~别问意义是什么~~

@git.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await git.finish(error(10))
    output = ""
    commit = args.extract_plain_text()
    if commit == "pull":
        output = os.popen("git pull").read()
        await git.finish(output)
    os.system("git add .")
    msg = ""
    msg = msg + os.popen("git commit -m \""
                         + commit
                         + "\""
                         ).read()
    msg = msg + os.popen("git push").read()
    if msg == "":
        msg = "执行完成，但没有输出哦~"
    await git.finish(msg)

voice = on_command("voice", force_whitespace=True, priority=5)  # 调用腾讯的语音TTS接口，生成语音。

@voice.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 10):
        await voice.finish(error(10))
    sth = args.extract_plain_text()
    final_msg = f"[CQ:tts,text={sth}]"
    await bot.call_api("send_group_msg", group_id=event.group_id, message=final_msg)

randomnum = on_command("random_num", aliases={"随机数"}, force_whitespace=True, priority=5)

@randomnum.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await randomnum.finish("唔……请参考下面的随机数生成格式：\n随机数 起始 终止")
    if not check_number(arg[0]) or not check_number(arg[1]):
        await randomnum.finish("唔……随机数的范围需要是数字哦~")
    num = random.randint(int(arg[0]), int(arg[1]))
    await randomnum.finish("好的，音卡已经为你生成了一个随机数：" + str(num))