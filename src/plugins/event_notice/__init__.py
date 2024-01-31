from src.tools.dep import *
from src.tools.config import Config
from src.tools.file import read, write
from src.tools.permission import checker, error
from src.tools.utils import checknumber

import nonebot
import json
import os

from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot import on_notice, on_command, on_request
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, NoticeEvent, RequestEvent
from nonebot.params import CommandArg


def banned(sb):  # 检测某个人是否被封禁。
    with open(bot_path.TOOLS + "/ban.json") as cache:
        banlist = json.loads(cache.read())
        for i in banlist:
            if i == sb:
                return True
        return False


notice = on_notice(priority=5)


def check_env_path(group_id: str):
    new_path = f"{bot_path.DATA}/{str(group_id)}"
    if os.path.exists(f"{new_path}/blacklist.json"):
        return True
    os.mkdir(new_path)
    write(f"{new_path }/jx3group.json", "{\"group\":\"" + str(group_id) +
          "\",\"server\":\"\",\"leader\":\"\",\"leaders\":[],\"name\":\"\",\"status\":false}")
    write(f"{new_path }/webhook.json", "[]")
    write(f"{new_path }/marry.json", "[]")
    write(f"{new_path }/banword.json", "[]")
    write(f"{new_path }/opening.json", "[]")
    write(f"{new_path }/wiki.json", "{\"startwiki\":\"\",\"interwiki\":[]}")
    write(f"{new_path }/arcaea.json", "{}")
    write(f"{new_path }/record.json", "[]")
    write(f"{new_path }/subscribe.json", "[]")
    write(f"{new_path }/blacklist.json", "[]")

    # 设置开始日期
    GroupConfig(group_id).mgr_property("auth.start", DateTime().timestamp())
    return False


@notice.handle()
async def on_new_group_enter(bot: Bot, event: NoticeEvent):
    """入群自动发送帮助信息。"""
    if not event.notice_type == "group_increase":
        return
    obj = event.user_id
    group = event.group_id
    bots = Config.bot
    config = GroupConfig(group)
    if str(obj) not in bots:
        msg = ms.at(obj) + config.mgr_property("templates.welcome")
        return await bot.call_api("send_group_msg", group_id=group, message=msg)

    if event.sub_type != "approve":
        return

    if check_env_path(event.group_id):
        return
    await bot.call_api("send_group_msg", group_id=event.group_id, message=f"检测到本群为新群聊，{Config.name}已经自动补全所需要的文件啦！")


@notice.handle()
async def on_group_ban(bot: Bot, event: NoticeEvent):
    """被禁言了"""
    if event.notice_type != "group_ban":
        return
    if str(event.user_id) not in Config.bot:
        return

    await bot.call_api("set_group_leave", group_id=event.group_id)
    return await notice_and_ban(bot, event, "禁言")


@notice.handle()
async def on_group_decrease(bot: Bot, event: NoticeEvent):
    """被踢了"""
    if not event.notice_type == "group_decrease":
        return
    if event.sub_type != "kick_me":
        return
    return await notice_and_ban(bot, event, "移出")


async def notice_and_ban(bot: Bot, event: NoticeEvent, action: str):
    message = f"唔……{Config.name}在群聊（{event.group_id}）被{action}啦！\n操作者：{event.operator_id}，已自动封禁！"
    for i in Config.notice_to:
        await bot.call_api("send_group_msg", group_id=int(i), message=message)
    kicker = str(event.operator_id)
    if banned(kicker):
        return
    banlist = json.loads(read(bot_path.TOOLS + "/ban.json"))
    banlist.append(kicker)
    write(bot_path.TOOLS + "/ban.json", json.dumps(banlist))
request = on_request(priority=5)


@request.handle()
async def _(bot: Bot, event: RequestEvent):
    if event.request_type == "group" and event.sub_type == "invite":
        msg = event.comment
        group = event.group_id
        user = event.user_id

        msg = f"收到新的加群申请：\n邀请人：{user}\n群号：{group}\n消息：{msg}"
        for i in Config.notice_to:

            await bot.call_api("send_group_msg", group_id=int(i), message=msg)

notice_cmd_welcome_msg_edit = on_command(
    "welcome",
    name="设置欢迎语",
    aliases={"设置入群欢迎语"},
    priority=5,
    description="设置入群欢迎语，不要有空格",
    catalog=permission.bot.command.mapper,
    example=[
        Jx3Arg(Jx3ArgsType.string, default="欢迎入群", alias="新欢迎语"),
    ],
    document="""
    欢迎语的修改。
    """
)


@notice_cmd_welcome_msg_edit.handle()
async def notice_welcome_msg_edit(bot: Bot, event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_msg, = args
    permission = checker(str(event.user_id), 5)
    if not permission and not group_admin:
        personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
        group_admin = personal_data["role"] in ["owner", "admin"]
        return await notice_cmd_welcome_msg_edit.finish(PROMPT_NoPermissionAdmin)

    config = GroupConfig(event.group_id)
    config.mgr_property("templates.welcome", arg_msg)
    return await notice_cmd_welcome_msg_edit.send(f"设置完成")
