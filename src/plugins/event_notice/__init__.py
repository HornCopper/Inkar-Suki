from typing import Union, Any

from nonebot import on_notice, on_command, on_request
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import (
    Bot, 
    GroupMessageEvent, 
    RequestEvent, 
    GroupIncreaseNoticeEvent, 
    GroupRequestEvent,
    GroupDecreaseNoticeEvent, 
    GroupBanNoticeEvent,
    MessageSegment as ms
)
from nonebot.params import CommandArg

from src.tools.config import Config
from src.tools.permission import checker, error
from src.tools.database import group_db, BannedList, ApplicationsList, GroupSettings
from src.tools.basic.group import getGroupSettings, setGroupSettings

from src.plugins.ban import banned

selfEnterMsg = """噔噔咚——音卡很荣幸受邀来到了「$GROUP_ID」~
请先告诉我这个群聊需要绑定哪一个区服呢？这样我才可以更好地为您服务☆
示例：绑定 幽月轮
订阅消息需要手动设置，如果需要请使用：订阅 开服
同时使用这个指令后，可以查看音卡所有的可订阅栏目哦，使用“订阅”后面跟上这些项目就可以订阅啦。

如需查看音卡的指令，请发送：帮助
其余注意事项可以查看音卡空间来了解哦，空间也将不定时发布活动等事项，敬请关注！"""


# 上述欢迎语内容为@厌睢(监狱牢头)制作，HornCopper修改

notice_to = Config.bot_basic.bot_notice

notice = on_notice(priority=5)


@notice.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    """入群自动发送帮助信息。"""
    obj = event.user_id
    group = event.group_id
    bots = notice_to
    if str(obj) not in bots:
        welcome_msg = getGroupSettings(str(event.group_id), "welcome")
        if not isinstance(welcome_msg, str):
            return
        msg = ms.at(obj) + " " + welcome_msg
        await bot.call_api("send_group_msg", group_id=group, message=msg)
        return
    await bot.call_api("send_group_msg", group_id=event.group_id, message=selfEnterMsg.replace("$GROUP_ID", str(event.group_id)))
    group_id = str(event.group_id)
    new_settings = GroupSettings(group_id=group_id)
    group_db.save(new_settings)

async def notice_and_ban(bot: Bot, event: Union[GroupDecreaseNoticeEvent, GroupBanNoticeEvent], action: str):
    message = f"唔……{Config.bot_basic.bot_name}在群聊（{event.group_id}）被{action}啦！\n操作者：{event.operator_id}，已自动封禁！"
    notice = notice_to
    await bot.call_api("send_group_msg", group_id=int(notice[str(event.self_id)]), message=message)
    kicker = str(event.operator_id)
    if banned(kicker):
        return
    banlist_obj: Union[BannedList, Any] = group_db.where_one(BannedList(), default=BannedList())
    banlist_data = banlist_obj.banned_list
    banlist_data.append({"uid": kicker, "reason": "T"})
    banlist_obj.banned_list = banlist_data
    group_db.save(banlist_obj)

@notice.handle()
async def _(bot: Bot, event: GroupBanNoticeEvent):
    """被禁言了"""
    if event.notice_type != "group_ban":
        return
    if str(event.user_id) not in notice_to:
        return
    await bot.call_api("set_group_leave", group_id=event.group_id)
    await notice_and_ban(bot, event, "禁言")


@notice.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
    """被踢了"""
    if not event.notice_type == "group_decrease":
        return
    if event.sub_type != "kick_me":
        return
    await notice_and_ban(bot, event, "移出")

request = on_request(priority=5)

@request.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    if event.request_type == "group" and event.sub_type == "invite":
        group = event.group_id
        user = event.user_id
        banned_data: Union[BannedList, Any] = group_db.where_one(BannedList(), default=BannedList())
        if str(user) in banned_data.banned_list:
            await bot.call_api("set_group_add_request", flag=event.flag, sub_type="invite", approve=False, reason="邀请人已被音卡封禁！无法邀请音卡入群！")
        flag = event.flag
        time = event.time
        new = {
            "group_id": group,
            "user_id": user,
            "flag": flag,
            "time": time
        }
        applications_data: Union[ApplicationsList, Any] = group_db.where_one(ApplicationsList(), default=ApplicationsList())
        applications_list = applications_data.applications_list
        if new in applications_list:
            return
        applications_list.append(new)
        applications_data.applications_list = applications_list
        group_db.save(applications_data)
        msg = f"收到新的加群申请：\n邀请人：{user}\n群号：{group}"
        await bot.call_api("send_group_msg", group_id=int(notice_to[str(event.self_id)]), message=msg)


notice_cmd_welcome_msg_edit = on_command("welcome", force_whitespace=True, priority=5)

@notice_cmd_welcome_msg_edit.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg_msg = args.extract_plain_text()
    permission = checker(str(event.user_id), 5)
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not permission and not group_admin:
        await notice_cmd_welcome_msg_edit.finish(error(5))
    setGroupSettings(str(event.group_id), "welcome", arg_msg)
    await notice_cmd_welcome_msg_edit.finish("好啦，已经设置完成啦！")
