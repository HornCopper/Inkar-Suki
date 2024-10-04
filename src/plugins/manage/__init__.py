from typing import Any

from nonebot import on_command
from nonebot.adapters import Message, Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.params import CommandArg, Arg, RawCommand

from src.config import Config
from src.const.path import (
    CACHE,
    build_path
)
from src.utils.network import Request
from src.utils.time import Time
from src.utils.permission import check_permission, denied
from src.utils.database import db
from src.utils.database.classes import GroupSettings, Account
from src.utils.database.operation import get_groups
from src.utils.message import post_process
from src.utils.exceptions import ConnectTimeout

from ._message import leave_msg

try:
    from .auto_accept import * # type: ignore
    # 仅用于公共实例，个人实例如有需要可自行创建`auto_accept.py`并写入逻辑。
except:
    pass

import os

DismissMatcher = on_command("dismiss", aliases={"移除音卡"}, force_whitespace=True, priority=5)


@DismissMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    user_permission = personal_data["role"] in ["owner", "admin"]
    if not (check_permission(str(event.user_id), 10) or user_permission):
        await DismissMatcher.finish(f"唔……只有群主或管理员才能移除{Config.bot_basic.bot_name}哦~")
    else:
        await DismissMatcher.send(f"确定要让{Config.bot_basic.bot_name}离开吗？如果是，请再发送一次“移除音卡”。")


@DismissMatcher.got("confirm")
async def _(bot: Bot, event: GroupMessageEvent, confirm: Message = Arg()):
    u_input = confirm.extract_plain_text()
    if u_input == "移除音卡":
        await DismissMatcher.send(leave_msg)
        await bot.call_api("send_group_msg", group_id=int(Config.bot_basic.bot_notice[str(event.self_id)]), message=f"{Config.bot_basic.bot_name}按他们的要求，离开了{event.group_id}。")
        await bot.call_api("set_group_leave", group_id=event.group_id)


ResetMatcher = on_command("recovery", aliases={"重置音卡"}, force_whitespace=True, priority=5)

@ResetMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    user_permission = personal_data["role"] in ["owner", "admin"]
    if not (check_permission(str(event.user_id), 10) or user_permission):
        await ResetMatcher.finish(f"唔……只有群主或管理员才能重置{Config.bot_basic.bot_name}哦~")
    else:
        await ResetMatcher.send(f"确定要重置{Config.bot_basic.bot_name}数据吗？如果是，请再发送一次“重置音卡”。\n注意：所有本群数据将会清空，包括绑定和订阅，该操作不可逆！")

@ResetMatcher.got("confirm")
async def _(bot: Bot, event: GroupMessageEvent, confirm: Message = Arg()):
    u_input = confirm.extract_plain_text()
    if u_input == "重置音卡":
        group_id = str(event.group_id)
        group_settings: GroupSettings | Any = db.where_one(GroupSettings(), "group_id = ?", group_id, default=None)
        group_settings = GroupSettings(id=group_settings.id, group_id=group_settings.group_id)
        db.save(group_settings)
        await DismissMatcher.send("重置成功！可以重新开始绑定本群数据了！")

github_token = Config.github.github_personal_token

async def create_issue(uin: str, comment: str):
    title = "【反馈】Inkar Suki · 使用反馈"
    date = Time().format()
    msg = f"日期：{date}\n用户：{uin}\n留言：{comment}"
    url = f"https://api.github.com/repos/{Config.bot_basic.bot_repo}/issues"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,
        "body": msg
    }
    await Request(url, headers=headers, params=data).post()

FeedbackMatcher = on_command("feedback", aliases={"反馈"}, force_whitespace=True, priority=5)

@FeedbackMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    msg = args.extract_plain_text()
    user = str(event.user_id)
    if len(msg) <= 8:
        await FeedbackMatcher.finish("唔……反馈至少需要8字以上，包括标点符号。")
    else:
        await create_issue(user, msg)
        await FeedbackMatcher.finish("已经将您的反馈内容提交至Inkar Suki GitHub，处理完毕后我们会通过电子邮件等方式通知您，音卡感谢您的反馈！")

EchoMatcher = on_command("echo", force_whitespace=True, priority=5)  # 复读只因功能

@EchoMatcher.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not check_permission(str(event.user_id), 10):
        await EchoMatcher.finish(denied(10))
    await EchoMatcher.finish(args)

PingMatcher = on_command("ping", force_whitespace=True, priority=5)  # 测试机器人是否在线

@PingMatcher.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    permission = check_permission(str(event.user_id), 1)
    if not permission:
        await PingMatcher.finish(f"咕咕咕，音卡来啦！\n当前时间为：{Time().format()}\n欢迎使用Inkar-Suki！")
    else:
        groups = await bot.call_api("get_group_list")
        group_count = len(groups)
        friends = await bot.call_api("get_friend_list")
        friend_count = len(friends)
        registers = get_groups()
        if not isinstance(registers, list):
            return
        register_count = len(registers)
        msg = f"咕咕咕，音卡来啦！\n现在是：{Time().format()}\n{group_count} | {register_count} | {friend_count}\n您拥有机器人的管理员权限！"
    await PingMatcher.finish(msg)

PurgeMatcher = on_command("purge", force_whitespace=True, priority=5)

@PurgeMatcher.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    if not check_permission(str(event.user_id), 10):
        await PurgeMatcher.finish(denied(10))
    try:
        for i in os.listdir(CACHE):
            os.remove(build_path(CACHE, [i]))
    except Exception as _:
        await PurgeMatcher.finish("部分文件并没有找到哦~")
    else:
        await PurgeMatcher.finish("好的，已帮你清除图片缓存~")

AdminMatcher = on_command("setop", aliases={"admin", "setadmin"}, force_whitespace=True, priority=5)

@AdminMatcher.handle()
async def _(bot: Bot, event: MessageEvent, full_argument: Message = CommandArg()):
    if full_argument.extract_plain_text() == "":
        return
    if not check_permission(str(event.user_id), 10) and str(event.user_id) not in Config.bot_basic.bot_owner:
        await AdminMatcher.finish(denied(10))
    args = full_argument.extract_plain_text().split(" ")
    user_id = args[0]
    if user_id in Config.bot_basic.bot_owner and str(event.user_id) not in Config.bot_basic.bot_owner:
        await AdminMatcher.finish("无法修改Bot主人的权限！")
    level = args[1]
    data: Account | Any = db.where_one(Account(), "user_id = ?", int(user_id), default=Account(user_id=int(user_id)))
    raw_permission = data.permission
    data.permission = int(level)
    db.save(data)
    await AdminMatcher.finish(f"用户（{user_id}）的权限等级已变更！\n{raw_permission} -> {level}")

@post_process
async def _(bot: Bot, event: MessageEvent, exception: None | Exception, cmd = RawCommand()):
    if cmd is None:
        return
    if exception:
        if isinstance(exception, ConnectTimeout):
            return # 不回了爱咋咋地
        if isinstance(event, GroupMessageEvent):
            await bot.call_api("send_group_msg", group_id=event.group_id, message=f"呜……音卡处理消息中遇到了代码错误，请将本消息告知开发者！\n{exception.__class__}: {exception}\n原始命令：\n{event.raw_message}")