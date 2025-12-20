from typing import Any

from nonebot import on_command, get_bots
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from src.utils.analyze import check_number
from src.utils.permission import check_permission
from src.utils.nonebot_plugins import scheduler
from src.utils.database.classes import GroupSettings
from src.utils.database import db
from src.utils.time import Time

from .app import get_expire_at, update_expire_time, is_within_48_hours

expire_at = on_command("查看授权", priority=5, force_whitespace=True)


@expire_at.handle()
async def _(event: GroupMessageEvent):
    expire_msg = get_expire_at(event.group_id)
    msg = f"本群（{event.group_id}）授权情况如下：\n{expire_msg}"
    await expire_at.finish(msg)


update_activation = on_command("授权", priority=5, force_whitespace=True)


@update_activation.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    days = args.extract_plain_text()
    if not check_number(days):
        await update_activation.finish(
            "请使用“授权 天数”，确保天数为数字！\n天数为纯数字，例如“30”而不是“30天”！"
        )
    if days == "-1" and not check_permission(event.user_id, 8):
        await update_activation.finish("权限不足，仅机器人管理员可设置永久授权！")
    msg = update_expire_time(event.group_id, int(days))
    await update_activation.finish(msg)


# @scheduler.scheduled_job("cron", hour="19", minute="0")
async def check_activation():
    bots = get_bots()
    database: list[GroupSettings] | Any = db.where_all(GroupSettings(), default=[])
    for bot in bots.values():
        account_groups: list[str] = [
            str(g["group_id"]) for g in (await bot.call_api("get_group_list"))
        ]
        database_groups: list[GroupSettings] = [
            g for g in database if g.group_id in account_groups
        ]
        for group in database_groups:
            if group.expire == 0:
                group.expire = Time().raw_time + 3 * 24 * 60 * 60
                db.save(group)
                continue
            elif group.expire == -1:
                continue
            else:
                pass
                if Time().raw_time > group.expire:
                    await bot.call_api("set_group_leave", group_id=int(group.group_id))
                if is_within_48_hours(group.expire):
                    await bot.call_api(
                        "send_group_msg",
                        group_id=int(group.group_id),
                        message="本群授权剩余不足48小时，请尽快进行授权！\n@任意音卡并输入“授权 天数”（最大30天）",
                    )
