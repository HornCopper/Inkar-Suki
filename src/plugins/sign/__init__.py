import sys
import nonebot
from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import Event, MessageSegment as ms
from nonebot.log import logger as l

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
CLOCK = TOOLS[:-5] + "clock"

from .manage import Sign
from file import read, write

'''
签到功能，仅供娱乐。

原理：定时任务 + 文件操作
'''

sign_main = Sign

sign_ = on_command("-签到", aliases={"-打卡"}, priority=5)
@sign_.handle()
async def sign(event: Event):
    if sign_main.wsigned(event.user_id):
        await sign_.finish(ms.at(event.user_id) + "\n你已经签到过了哦，不能重复签到。")
    data = sign_main.generate_everyday_reward()
    coin = data["coin"]
    luck = data["luck"]
    if luck == 0:
        luck = "末吉签（1x）"
    elif luck == 1:
        luck = "中吉签（2x）"
    elif luck == 2:
        luck = "上吉签（3x）"
    else:
        luck = "上上签（4x）"
    s = data["signed"] + 1
    wlottery = data["wlottery"]
    msg = ms.at(event.user_id) + f"\n签到成功！\n金币：+{coin}\n今日运势：{luck}"
    if wlottery:
        msg = msg + "\n触发额外奖励！已帮你额外添加了100枚金币！"
    sign_main.save_data(data, event.user_id)
    continuity_day = sign_main.get_continuity(event.user_id)
    if continuity_day != False:
        msg = msg + f"\n已连续签到{continuity_day}天！"
    msg = msg + f"\n在所有群内，您是第{s}位签到的哦~"
    await sign_.finish(msg)

coin = on_command("金币", aliases={"余额"}, priority=5)
@coin.handle()
async def sign(event: Event):
    coin_ = Sign.get_coin(event.user_id)
    if coin_ == False:
        await coin.finish("唔……您没有签到过哦，没有任何金币余额呢！")
    else:
        await coin.finish(ms.at(event.user_id) + f"\n您的金币余额为：\n{coin_}枚")

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

@scheduler.scheduled_job("cron", hour="7")
async def clean_data():
    write(CLOCK + "/signed.json","[]")
    l.info("Signed.json has been cleaned.")
    