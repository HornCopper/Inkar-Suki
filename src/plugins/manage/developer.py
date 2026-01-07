from typing import Any

from nonebot import on_command
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent

from src.config import Config
from src.utils.permission import check_permission
from src.utils.generate import generate
from src.utils.database import db
from src.utils.database.classes import Account, GroupSettings

import json

ScreenShotMatcher = on_command("screenshot", priority=5, force_whitespace=True)

@ScreenShotMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    url = args.extract_plain_text()
    if not url.startswith("http"):
        return
    if not check_permission(event.user_id, 8):
        return
    try:
        image = await generate(url, full_screen=True, viewport={"height": 1080, "width": 1920}, segment=True)
    except:  # noqa: E722
        await ScreenShotMatcher.finish("Screenshot Failed!")
    await ScreenShotMatcher.finish(image)

ResetGlobalPermissionMatcher = on_command("重置权限", priority=5, force_whitespace=True)

@ResetGlobalPermissionMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.user_id) not in Config.bot_basic.bot_owner:
        return
    await ResetGlobalPermissionMatcher.send("确定要重置所有人的权限吗？\n警告：请确认自己在做什么！如果确认无误，请发送“确认重置权限”。")

@ResetGlobalPermissionMatcher.got("confirm")
async def _(event: GroupMessageEvent, confirm: Message = Arg()):
    u_input = confirm.extract_plain_text()
    if u_input == "确认重置权限":
        all_accounts: list[Account] | Any = db.where_all(Account())
        for account in all_accounts:
            account.permission = 0
            db.save(account)
    await ResetGlobalPermissionMatcher.finish("已重置所有人的权限！")

ResetGlobalCoinMatcher = on_command("重置货币", priority=5, force_whitespace=True)

@ResetGlobalCoinMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.user_id) not in Config.bot_basic.bot_owner:
        return
    await ResetGlobalCoinMatcher.send("确定要重置所有人的货币吗？\n警告：请确认自己在做什么！如果确认无误，请发送“确认重置货币”。")

@ResetGlobalCoinMatcher.got("confirm")
async def _(event: GroupMessageEvent, confirm: Message = Arg()):
    u_input = confirm.extract_plain_text()
    if u_input == "确认重置货币":
        all_accounts: list[Account] | Any = db.where_all(Account())
        for account in all_accounts:
            account.coins = 0
            db.save(account)
    await ResetGlobalCoinMatcher.finish("已重置所有人的货币！")

SetInvitorMatcher = on_command("设置邀请人", priority=5, force_whitespace=True)

@SetInvitorMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if not check_permission(event.user_id, 8):
        return
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await SetInvitorMatcher.finish("格式错误：设置邀请人 群号 QQ号")
    group_id = arg[0]
    user_id = arg[1]
    current_setting: GroupSettings | Any = db.where_one(GroupSettings(), "group_id = ?", group_id, default=GroupSettings(group_id=group_id))
    current_setting.invitor = int(user_id)
    db.save(current_setting)
    await SetInvitorMatcher.finish(f"成功设置群[{group_id}]的邀请人为[{user_id}]！")

onebot_api_call = on_command("调用API", priority=5, force_whitespace=True)

@onebot_api_call.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if not check_permission(event.user_id, 10):
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) < 2:
        return
    api = arg[0]
    params = json.loads(" ".join(arg[1:]))
    await bot.call_api(api, **params)