import sys
from src.tools.dep import *
from src.tools.file import read, write

from .manage import Sign

'''
签到功能，仅供娱乐。

原理：定时任务 + 文件操作
'''

sign_main = Sign

sign_ = on_command("-签到", aliases={"-打卡"}, priority=5)
@sign_.handle()
async def sign(event: Event):
    if sign_main.wsigned(event.user_id):
        return await sign_.finish(ms.at(event.user_id) + "\n你已经签到过了哦，不能重复签到。")
    data = sign_main.generate_everyday_reward(event.user_id)

    sign_main.save_data(data, event.user_id)
    await sign_.finish(data.msg)

coin = on_command("金币", aliases={"余额"}, priority=5)
@coin.handle()
async def check_balance(event: Event):
    coin_ = Sign.get_coin(event.user_id)
    if coin_ == False:
        return await coin.finish("唔……您没有签到过哦，没有任何金币余额呢！")
    return await coin.finish(ms.at(event.user_id) + f"\n您的金币余额为：\n{coin_}枚")

@scheduler.scheduled_job("cron", hour="7")
async def clean_data():
    write(CLOCK + "/signed.json","[]")
    logger.info("Signed.json has been cleaned.")
    try:
        for i in os.listdir(CACHE):
            os.remove(CACHE + "/" + i)
        logger.info("已清理所有缓存文件。")
    except:
        logger.info("缓存清理失败，请检查后重试！！！")
    