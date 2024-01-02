from src.tools.dep import *
from .SubscribeItem import *


async def OnDefaultCallback(bot: Bot, group_id: str, sub: SubscribeSubject, cron: SubjectCron):
    message = cron.notify_content
    return message


async def OnWorldBoss(bot: Bot, group_id: str, sub: SubscribeSubject, cron: SubjectCron):
    return await OnDefaultCallback(bot, group_id, sub, cron)


async def OnGfBig(bot: Bot, group_id: str, sub: SubscribeSubject, cron: SubjectCron):
    return await OnDefaultCallback(bot, group_id, sub, cron)


async def OnGfSmall(bot: Bot, group_id: str, sub: SubscribeSubject, cron: SubjectCron):
    return await OnDefaultCallback(bot, group_id, sub, cron)
