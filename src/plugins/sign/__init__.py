from src.tools.basic import *
from src.tools.file import write

from .manage import Sign

from nonebot_plugin_apscheduler import scheduler

"""
签到功能，仅供娱乐。

原理：定时任务 + 文件操作
"""

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Event, Message
from nonebot.params import Arg, CommandArg, ArgPlainText
from .message import message_sign

import random

command = on_command("抽签", priority=6)
@command.handle()
async def lq_():
    await command.send("确定要抽取吗")

@command.got("pb")
async def pq_(reply: str = ArgPlainText("pb")):
    if reply == "确定" or "yes" or "抽取" or "嗯":
        for i in range(3):
            a = random.randint(0,100)
            if a >= 5 :
                pd=True
                await command.send(
                    message="抽到了正签"
                )
                break
            else:#为了模拟真实抛杯才设置空签
                await command.send(
                    message="是空签呢",
                    at_sender=True,
                )
                pd=False
                break

        if pd is True:
            await command.finish(message=f"\n{random.choice(message_sign)}",at_sender=True)
        else:
           await command.finish()
    else:
        await command.finish("\n放弃了抽取",at_sender=True,)

sign_main = Sign

sign_ = on_command("签到", aliases={"打卡"}, priority=5)


@sign_.handle()
async def sign(event: Event):
    if sign_main.wsigned(event.user_id):
        await sign_.finish(ms.at(event.user_id) + "\n你已经签到过了哦，不能重复签到。")
    data = sign_main.generate_everyday_reward(event.user_id)

    sign_main.save_data(data, event.user_id)
    await sign_.finish(data.msg)

coin_ = on_command("金币", aliases={"余额"}, priority=5)


@coin_.handle()
async def check_balance(event: Event):
    coin__ = Sign.get_coin(event.user_id)
    if coin_ is False:
        await coin_.finish("唔……您没有签到过哦，没有任何金币余额呢！")
    await coin_.finish(ms.at(event.user_id) + f"\n您的金币余额为：\n{coin__}枚")


addc = on_command("增加金币", priority=5)

@addc.handle()
async def _(event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id), 10) == False:
        await addc.finish(error(10))
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await addc.finish("唔……参数数量不正确哦~")
    if not checknumber(arg[0]) or not checknumber(arg[1]):
        await addc.finish("唔……参数需要是数字哦~")
    Sign.add(arg[0], arg[1])
    await addc.finish("已向该账户添加了" + arg[1] + "枚金币！")

reducec = on_command("减少金币", priority=5)

@reducec.handle()
async def _(event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id), 10) == False:
        await reducec.finish(error(10))
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await reducec.finish("唔……参数数量不正确哦~")
    if not checknumber(arg[0]) or not checknumber(arg[1]):
        await reducec.finish("唔……参数需要是数字哦~")
    Sign.reduce(arg[0], arg[1])
    await reducec.finish("已向该账户扣除了" + arg[1] + "枚金币！")

@scheduler.scheduled_job("cron", hour="7")
async def clean_data():
    write(CLOCK + "/signed.json", "[]")
    logger.info("Signed.json has been cleaned.")
    try:
        for i in os.listdir(CACHE):
            os.remove(CACHE + "/" + i)
        logger.info("已清理所有缓存文件。")
    except Exception as _:
        logger.info("缓存清理失败，请检查后重试！！！")
