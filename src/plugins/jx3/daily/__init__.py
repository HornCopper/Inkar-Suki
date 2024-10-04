from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from src.utils.nonebot_plugins import scheduler
from src.utils.database.operation import send_subscribe

from .api import get_daily_info

import datetime

DailyMatcher = on_command("jx3_daily", aliases={"日常"}, force_whitespace=True, priority=5)
@DailyMatcher.handle()
async def _(event: GroupMessageEvent):
    msg = await get_daily_info()
    await DailyMatcher.finish(msg)

@scheduler.scheduled_job("cron", hour="8", minute="30")
async def run_at_8_30():
    msg = await get_daily_info()
    msg = "早安！音卡为您送上今天的日常：\n" + msg
    await send_subscribe("日常", msg)

@scheduler.scheduled_job("cron", hour="19", minute="30")
async def boss():
    if datetime.date.today().weekday() in [2, 4]:
        activity = "世界BOSS（主20:00/分20:05）"
    else:
        return
    msg = activity + "即将开始，请提前到达对应地图等待吧！"
    await send_subscribe("世界BOSS", msg)

@scheduler.scheduled_job("cron", hour="19", minute="20")
async def small_gf():
    if datetime.date.today().weekday() in [1, 3]:
        activity = "逐鹿中原"
    else:
        return
    msg = activity + "即将开始，请提前到达对应地图等待吧！"
    await send_subscribe("攻防", msg)

@scheduler.scheduled_job("cron", hour="18", minute="20")
@scheduler.scheduled_job("cron", hour="12", minute="20")
async def gf_notice():
    if datetime.date.today().weekday() == 6:
        map = "恶人谷"
    elif datetime.date.today().weekday() == 5:
        map = "浩气盟"
    else:
        return
    msg = f"阵营攻防还有40分钟开始啦，请提前半小时进入 {map} 地图！"
    await send_subscribe("攻防", msg)