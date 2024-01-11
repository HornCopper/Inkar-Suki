from .SubscribeItem import *


async def OnDefaultCallback(group_id: str, sub: SubscribeSubject, cron: SubjectCron):
    message = cron.notify_content
    return message


async def OnWorldBoss(group_id: str, sub: SubscribeSubject, cron: SubjectCron):
    return await OnDefaultCallback(group_id, sub, cron)


async def OnGfBig(group_id: str, sub: SubscribeSubject, cron: SubjectCron):
    return await OnDefaultCallback(group_id, sub, cron)


async def OnGfSmall(group_id: str, sub: SubscribeSubject, cron: SubjectCron):
    return await OnDefaultCallback(group_id, sub, cron)
