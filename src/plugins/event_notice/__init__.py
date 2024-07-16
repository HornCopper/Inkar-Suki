from src.tools.basic import *
from src.tools.config import Config
from src.tools.file import read, write
from src.tools.permission import checker, error
from src.tools.utils import checknumber
from src.tools.utils.markdown import Markdown as md, send_markdown

import json
import os

from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot import on_notice, on_command, on_request
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, NoticeEvent, RequestEvent
from nonebot.params import CommandArg

selfEnterMsg = """噔噔咚——音卡很荣幸受邀来到了「$GROUP_ID」~
请先告诉我这个群聊需要绑定哪一个区服呢？这样我才可以更好地为您服务☆
示例：绑定 幽月轮
订阅消息需要手动设置，如果需要请使用：订阅 开服
同时使用这个指令后，可以查看音卡所有的可订阅栏目哦，使用“订阅”后面跟上这些项目就可以订阅啦。

如需查看音卡的指令，请发送：帮助
其余注意事项可以查看音卡空间来了解哦，空间也将不定时发布活动等事项，敬请关注！"""


# 上述欢迎语内容为@厌睢(监狱牢头)制作，HornCopper修改

def banned(sb):  # 检测某个人是否被封禁。
    with open(TOOLS + "/ban.json") as cache:
        banlist = json.loads(cache.read())
        for i in banlist:
            if i == sb:
                return True
        return False


notice = on_notice(priority=5)


@notice.handle()
async def _(bot: Bot, event: NoticeEvent):
    """入群自动发送帮助信息。"""
    if event.notice_type != "group_increase":
        return
    obj = event.user_id
    group = event.group_id
    bots = Config.bot_basic.bot_notice
    if str(obj) not in bots:
        msg = ms.at(obj) + " " + getGroupData(str(event.group_id), "welcome")
        await bot.call_api("send_group_msg", group_id=group, message=msg)
        return
    await bot.call_api("send_group_msg", group_id=event.group_id, message=selfEnterMsg.replace("$GROUP_ID", str(event.group_id)))
    group_id = str(event.group_id)
    files = {
        "blacklist.json": [],
        "settings.json": {"server": "", "group": group_id, "subscribe": [], "addtions": [], "welcome": "欢迎入群！"},
        "webhook.json": [],
        "opening.json": [],
        "wiki.json": {"startwiki":"","interwiki":[]},
        "record.json": []
    }
    status = []
    for i in list(files):
        if os.path.exists(DATA + "/" + group_id + "/" + i):
            status.append(True)
            continue
        status.append(False)
        write(DATA + "/" + group_id + "/" + i, json.dumps(files[i]))


@notice.handle()
async def _(bot: Bot, event: NoticeEvent):
    """被禁言了"""
    if event.notice_type != "group_ban":
        return
    if str(event.user_id) not in Config.bot_basic.bot_notice:
        return
    await bot.call_api("set_group_leave", group_id=event.group_id)
    await notice_and_ban(bot, event, "禁言")


@notice.handle()
async def _(bot: Bot, event: NoticeEvent):
    """被踢了"""
    if not event.notice_type == "group_decrease":
        return
    if event.sub_type != "kick_me":
        return
    await notice_and_ban(bot, event, "移出")


async def _(bot: Bot, event: NoticeEvent, action: str):
    message = f"唔……{Config.bot_basic.bot_name}在群聊（{event.group_id}）被{action}啦！\n操作者：{event.operator_id}，已自动封禁！"
    for i in Config.bot_basic.bot_notice[str(event.self_id)]:
        await bot.call_api("send_group_msg", group_id=int(i), message=message)
    kicker = str(event.operator_id)
    if banned(kicker):
        return
    banlist = json.loads(read(TOOLS + "/ban.json"))
    banlist.append(kicker)
    write(TOOLS + "/ban.json", json.dumps(banlist))


# request = on_request(priority=5)


# @request.handle()
# async def _(bot: Bot, event: RequestEvent):
#     if event.request_type == "group" and event.sub_type == "invite":
#         group = event.group_id
#         user = event.user_id
#         if str(user) in json.loads(read(TOOLS + "/ban.json")):
#             await bot.call_api("set_group_add_request", flag=event.flag, sub_type="invite", approve=False, reason="邀请人已被音卡封禁！无法邀请音卡入群！")
#         flag = event.flag
#         time = event.time
#         new = {
#             "group_id": group,
#             "user_id": user,
#             "flag": flag,
#             "time": time
#         }
#         current = json.loads(read(TOOLS + "/" + "application.json"))
#         if new in current:
#             return
#         current.append(new)
#         write(TOOLS + "/" + "application.json", json.dumps(current, ensure_ascii=False))
#         btn_accept = md.button("同意", "同意申请 " + str(group))
#         btn_deny = md.button("拒绝", "拒绝申请 " + str(group))
#         msg = (f"# 收到新的加群申请：\n"
#                f"邀请人：{user}\n"
#                f"群号：{group}\n\n"
#                f"> {btn_accept}    {btn_deny}")
#         for i in Config.bot_basic.bot_notice:
#             # await bot.call_api("send_group_msg", group_id=int(i), message=msg)
#             await send_markdown(msg, bot, session_id=int(i), message_type="group")

request = on_request(priority=5)

@request.handle()
async def _(bot: Bot, event: RequestEvent):
    if event.request_type == "group" and event.sub_type == "invite":
        group = event.group_id
        user = event.user_id
        if str(user) in json.loads(read(TOOLS + "/ban.json")):
            await bot.call_api("set_group_add_request", flag=event.flag, sub_type="invite", approve=False, reason="邀请人已被音卡封禁！无法邀请音卡入群！")
        flag = event.flag
        time = event.time
        new = {
            "group_id": group,
            "user_id": user,
            "flag": flag,
            "time": time
        }
        current = json.loads(read(TOOLS + "/" + "application.json"))
        if new in current:
            return
        current.append(new)
        write(TOOLS + "/" + "application.json", json.dumps(current, ensure_ascii=False))
        msg = f"收到新的加群申请：\n邀请人：{user}\n群号：{group}"
        for i in Config.bot_basic.bot_notice[str(event.self_id)]:
            await bot.call_api("send_group_msg", group_id=int(i), message=msg)


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
    setGroupData(str(event.group_id), "welcome", arg_msg)
    await notice_cmd_welcome_msg_edit.finish("好啦，已经设置完成啦！")
