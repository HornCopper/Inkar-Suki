from nonebot import on_command
from nonebot.adapters import Message, Bot
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg

from src.config import Config
from src.const.prompts import PROMPT
from src.utils.analyze import check_number
from src.utils.permission import check_permission, denied
from src.utils.message import message_universal

from .process import Ban

BanMatcher = on_command("ban", force_whitespace=True, priority=5)


@BanMatcher.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not check_permission(str(event.user_id), 10):
        await BanMatcher.finish(denied(10))
    user_id = args.extract_plain_text()
    if not check_number(user_id):
        await BanMatcher.finish(PROMPT.ArgumentInvalid)    
    status = Ban(event.user_id).ban()
    if not status:
        await BanMatcher.finish(PROMPT.BanRepeatInvalid)
    await BanMatcher.finish(f"好的，{Config.bot_basic.bot_name}已经封禁({user_id})！")

UnbanMatcher = on_command("unban", force_whitespace=True, priority=5)

@UnbanMatcher.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not check_permission(str(event.user_id), 10):
        await UnbanMatcher.finish(denied(10))
    user_id = args.extract_plain_text()
    if not check_number(user_id):
        await UnbanMatcher.finish(PROMPT.ArgumentInvalid)    
    status = Ban(event.user_id).unban()
    if not status:
        await UnbanMatcher.finish(PROMPT.BanRepeatInvalid)
    await UnbanMatcher.finish(f"好的，已经全域解封({user_id})。")


@message_universal.handle()
async def _(matcher: Matcher, event: MessageEvent):
    if Ban(event.user_id).status:
        matcher.stop_propagation()