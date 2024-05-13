from .api import *

from nonebot import require, get_bot

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

jx3_cmd_daily = on_command("jx3_daily", aliases={"日常"}, force_whitespace=True, priority=5)
@jx3_cmd_daily.handle()
async def jx3_daily(event: GroupMessageEvent):
    """
    查询日常。

    Notice：每个服务器的日常相同，仅美人图有可能存在不同。

    Example：-日常
    Example：-周常
    """
    info = await daily_()
    await jx3_cmd_daily.finish(info)