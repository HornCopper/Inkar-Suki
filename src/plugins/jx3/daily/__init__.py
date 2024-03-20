from .api import *

from nonebot import require, get_bot

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

jx3_cmd_daily = on_command("jx3_daily", aliases={"日常", "周常"}, priority=5)
@jx3_cmd_daily.handle()
async def jx3_daily(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询日常。

    Notice：每个服务器的日常相同，仅美人图有可能存在不同。

    Example：-日常
    Example：-周常
    Example：-日常 幽月轮
    """
    info = await daily_(args.extract_plain_text(), group_id = event.group_id)
    await jx3_cmd_daily.finish(info)

@scheduler.scheduled_job("cron", hour="7", minute="40", id="daily")
async def run_every_2_hour():
    msg = await daily_("幽月轮", Config.notice_to[0])
    bot = get_bot(int(Config.bot[0]))
    groups = os.listdir(DATA)
    for i in groups:
        subscribe = getGroupData(i, "subscribe")
        if "日常" in subscribe:
            await bot.call_api("send_group_msg", group_id=int(i), message=msg)