from typing import Any

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageEvent,
    Bot,
    Message,
    MessageSegment as ms
)
from nonebot.params import CommandArg, Arg, RawCommand
from nonebot.matcher import Matcher

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
from src.utils.database.operation import get_groups, get_group_settings
from src.utils.message import post_process
from src.utils.exceptions import ConnectTimeout
from src.utils.message import message_universal

from ._message import leave_msg
from .developer import *  # noqa: F403

try:
    from .auto_accept import *  # type: ignore  # noqa: F403
    # 仅用于公共实例，个人实例如有需要可自行创建`auto_accept.py`并写入逻辑。
except:  # noqa: E722
    pass

import os
import random

DismissMatcher = on_command("dismiss", aliases={"移除音卡"}, force_whitespace=True, priority=5)


@DismissMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    user_permission = personal_data["role"] in ["owner", "admin"]
    if not (check_permission(str(event.user_id), 9) or user_permission):
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
    if not (check_permission(str(event.user_id), 9) or user_permission):
        await ResetMatcher.finish(f"唔……只有群主或管理员才能重置{Config.bot_basic.bot_name}哦~")
    else:
        await ResetMatcher.send(f"确定要重置{Config.bot_basic.bot_name}数据吗？如果是，请再发送一次“重置音卡”。\n注意：所有本群数据将会清空，包括绑定、订阅和邀请人等，该操作不可逆！")

@ResetMatcher.got("confirm")
async def _(bot: Bot, event: GroupMessageEvent, confirm: Message = Arg()):
    u_input = confirm.extract_plain_text()
    if u_input == "重置音卡":
        db.delete(GroupSettings(), "group_id = ?", str(event.group_id))
        group_settings = GroupSettings(group_id=str(event.group_id))
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

EchoMatcher = on_command("echo", force_whitespace=True, priority=5)  # 复读机功能

@EchoMatcher.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not check_permission(str(event.user_id), 8):
        await EchoMatcher.finish(denied(8))
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
    not_owner = str(event.user_id) not in Config.bot_basic.bot_owner
    if not check_permission(str(event.user_id), 8) and not_owner:
        await AdminMatcher.finish(denied(10))
    args = full_argument.extract_plain_text().split(" ")
    user_id = args[0]
    if user_id in Config.bot_basic.bot_owner and not_owner:
        await AdminMatcher.finish("无法修改Bot主人的权限！")
    level = args[1]
    if not check_permission(event.user_id, int(level)-1) and not_owner:
        await AdminMatcher.finish("无法将权限提升至比自身更高的权限！")
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

async def get_emoji():
    api = "https://cms.jx3box.com/api/cms/post/emotions?type=&search=&star=&original=&page=1&per=50"
    data = (await Request(api).get()).json()
    data = data["data"]["list"]
    rdnum = random.randint(0, len(data) - 1)
    response = (await Request(data[rdnum]["url"]).get())
    if response.status_code == 200:
        return ms.image(data[rdnum]["url"])
    return None

@message_universal.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    group_subscribes = get_group_settings(event.group_id, "subscribe")
    group_additions = get_group_settings(event.group_id, "additions")
    if "禁言" in group_additions and "退订" not in event.raw_message and not event.raw_message.startswith("ping"):
        matcher.stop_propagation()
        return
    if "骚话" in group_subscribes and random.random() < 0.04: # 4%
        t = random.randint(0, 1)
        if t:
            data = (await Request("https://www.jx3api.com/data/saohua/random").get()).json()
            msg = data["data"]["text"]
            await bot.send_group_msg(group_id=event.group_id, message=msg)
        else:
            image = Message(await get_emoji())
            if image is None:
                return
            await bot.send_group_msg(group_id=event.group_id, message=image)