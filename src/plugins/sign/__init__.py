from src.tools.basic import *
from src.tools.file import write

from .manage import Sign

from nonebot_plugin_apscheduler import scheduler

"""
签到功能，仅供娱乐。

原理：定时任务 + 文件操作
"""

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
