from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .api import pendant

PendentMatcher = on_command("jx3_pendents", aliases={"挂件"}, force_whitespace=True, priority=5)


@PendentMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    await PendentMatcher.finish(await pendant(name=args.extract_plain_text()))