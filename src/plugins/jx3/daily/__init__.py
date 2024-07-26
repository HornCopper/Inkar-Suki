from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from nonebot import require, get_bots
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from src.tools.basic.group_opeator import getAllGroups, getGroupSettings

from .api import *

import datetime

jx3_cmd_daily = on_command("jx3_daily", aliases={"日常"}, force_whitespace=True, priority=5)
@jx3_cmd_daily.handle()
async def _(event: GroupMessageEvent):
    """
    查询日常。

    Notice：每个服务器的日常相同，仅美人图有可能存在不同。

    Example：-日常
    Example：-周常
    """
    info = await daily_()
    await jx3_cmd_daily.finish(info)

@scheduler.scheduled_job("cron", hour="8", minute="30")
async def run_at_8_30():
    msg = await daily_()
    msg = "早安！音卡为您送上今天的日常：\n" + msg
    bots = get_bots()
    groups = getAllGroups()
    group = {}
    for i in list(bots):
        single_groups = await bots[i].call_api("get_group_list")
        group_id_s = []
        for x in single_groups:
            group_id_s.append(x["group_id"])
        group[i] = group_id_s
    for group_id in groups:
        for x in list(group):
            if int(group_id) in group[x]:
                if "日常" in getGroupSettings(str(group_id), "subscribe"):
                    await bots[x].call_api("send_group_msg", group_id=int(group_id), message=msg)

@scheduler.scheduled_job("cron", hour="19", minute="30")
async def boss():
    if datetime.date.today().weekday() in [2, 4]:
        activity = "世界BOSS（主20:00/分20:05）"
    else:
        return
    msg = activity + "即将开始，请提前到达对应地图等待吧！"
    bots = get_bots()
    groups = getAllGroups()
    group = {}
    for i in list(bots):
        single_groups = await bots[i].call_api("get_group_list")
        group_id_s = []
        for x in single_groups:
            group_id_s.append(x["group_id"])
        group[i] = group_id_s
    for group_id in groups:
        for x in list(group):
            if int(group_id) in group[x]:
                if "世界BOSS" in getGroupSettings(str(group_id), "subscribe"):
                    await bots[x].call_api("send_group_msg", group_id=int(group_id), message=msg)

@scheduler.scheduled_job("cron", hour="19", minute="20")
async def small_gf():
    if datetime.date.today().weekday() in [1, 3]:
        activity = "逐鹿中原"
    else:
        return
    msg = activity + "即将开始，请提前到达对应地图等待吧！"
    bots = get_bots()
    groups = getAllGroups()
    group = {}
    for i in list(bots):
        single_groups = await bots[i].call_api("get_group_list")
        group_id_s = []
        for x in single_groups:
            group_id_s.append(x["group_id"])
        group[i] = group_id_s
    for group_id in groups:
        for x in list(group):
            if int(group_id) in group[x]:
                if "攻防" in getGroupSettings(str(group_id), "subscribe"):
                    await bots[x].call_api("send_group_msg", group_id=int(group_id), message=msg)

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
    bots = get_bots()
    groups = getAllGroups()
    group = {}
    for i in list(bots):
        single_groups = await bots[i].call_api("get_group_list")
        group_id_s = []
        for x in single_groups:
            group_id_s.append(x["group_id"])
        group[i] = group_id_s
    for group_id in groups:
        for x in list(group):
            if int(group_id) in group[x]:
                if "攻防" in getGroupSettings(str(group_id), "subscribe"):
                    await bots[x].call_api("send_group_msg", group_id=int(group_id), message=msg)