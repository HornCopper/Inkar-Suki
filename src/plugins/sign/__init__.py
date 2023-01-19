import json
import sys
import nonebot
from nonebot import on_command, require
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot, MessageSegment as ms
from nonebot.params import CommandArg
from nonebot.log import logger as l

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
SIGN = TOOLS[:-5] + "sign"

from .manage import Sign
from file import read, write


sign_main = Sign

sign_ = on_command("签到", aliases={"打卡"}, priority=5)
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

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

@scheduler.scheduled_job("cron", hour="7")
async def clean_data():
    write(SIGN + "/signed.json","[]")
    l.info("Signed.json has been cleaned.")
    