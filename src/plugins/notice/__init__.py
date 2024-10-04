from typing import Any

from nonebot import on_notice, on_command, on_request
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import (
    Bot, 
    GroupMessageEvent,
    GroupIncreaseNoticeEvent, 
    GroupRequestEvent,
    GroupDecreaseNoticeEvent, 
    GroupBanNoticeEvent,
    PokeNotifyEvent,
    MessageSegment as ms
)
from nonebot.params import CommandArg

from src.config import Config
from src.utils.permission import check_permission, denied
from src.utils.database import db
from src.utils.database.classes import BannedUser, ApplicationsList, GroupSettings
from src.utils.database.operation import get_group_settings, set_group_settings

from src.plugins.ban.process import Ban

from ._message import self_enter_msg

notice_to = Config.bot_basic.bot_notice

notice = on_notice(priority=5)

@notice.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    """入群自动发送帮助信息。"""
    obj = event.user_id
    group = event.group_id
    bots = notice_to
    if str(obj) not in bots:
        welcome_msg = get_group_settings(str(event.group_id), "welcome")
        if not isinstance(welcome_msg, str):
            return
        msg = ms.at(obj) + " " + welcome_msg
        await bot.call_api("send_group_msg", group_id=group, message=msg)
        return
    await bot.call_api("send_group_msg", group_id=event.group_id, message=self_enter_msg.replace("$GROUP_ID", str(event.group_id)))
    group_id = str(event.group_id)
    new_settings = GroupSettings(group_id=group_id)
    db.save(new_settings)

async def notice_and_ban(bot: Bot, event: GroupDecreaseNoticeEvent | GroupBanNoticeEvent, action: str):
    message = f"唔……{Config.bot_basic.bot_name}在群聊（{event.group_id}）被{action}啦！\n操作者：{event.operator_id}，已自动封禁！"
    notice = notice_to
    if Ban(event.operator_id).status:
        return
    banlist_obj: BannedUser = BannedUser(user_id=event.operator_id, reason="T")
    db.save(banlist_obj)
    await bot.call_api("send_group_msg", group_id=int(notice[str(event.self_id)]), message=message)

@notice.handle()
async def _(bot: Bot, event: GroupBanNoticeEvent):
    """禁言"""
    if event.notice_type != "group_ban":
        return
    if str(event.user_id) not in notice_to:
        return
    await bot.call_api("set_group_leave", group_id=event.group_id)
    await notice_and_ban(bot, event, "禁言")


@notice.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
    """移出"""
    if not event.notice_type == "group_decrease":
        return
    if event.sub_type != "kick_me":
        return
    await notice_and_ban(bot, event, "移出")

@notice.handle()
async def _(event: PokeNotifyEvent):
    if event.group_id is None or str(event.target_id) not in list(Config.bot_basic.bot_notice):
        return
    else:
        await notice.finish("音卡在呢！找音卡有什么事吗！(^ω^)" + ms.image("https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/emoji.jpg"))

request = on_request(priority=5)

@request.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    if event.request_type == "group" and event.sub_type == "invite":
        group = event.group_id
        user = event.user_id
        if Ban(event.user_id).status:
            await bot.call_api("set_group_add_request", flag=event.flag, sub_type="invite", approve=False, reason="邀请人已被音卡封禁！无法邀请音卡入群！")
        flag = event.flag
        time = event.time
        new = {
            "group_id": group,
            "user_id": user,
            "flag": flag,
            "time": time
        }
        applications_data: ApplicationsList | Any = db.where_one(ApplicationsList(), default=ApplicationsList())
        applications_list = applications_data.applications_list
        if new in applications_list:
            return
        applications_list.append(new)
        applications_data.applications_list = applications_list
        db.save(applications_data)
        msg = f"收到新的加群申请：\n邀请人：{user}\n群号：{group}"
        await bot.call_api("send_group_msg", group_id=int(notice_to[str(event.self_id)]), message=msg)


WelcomeEditMatcher = on_command("welcome", force_whitespace=True, priority=5)

@WelcomeEditMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg_msg = args.extract_plain_text()
    permission = check_permission(str(event.user_id), 5)
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not permission and not group_admin:
        await WelcomeEditMatcher.finish(denied(5))
    set_group_settings(str(event.group_id), "welcome", arg_msg)
    await WelcomeEditMatcher.finish("好啦，已经设置完成啦！")
