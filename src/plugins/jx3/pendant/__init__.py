from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from src.tools.config import Config

from .api import pendant

pendents = on_command("jx3_pendents", aliases={"挂件"}, force_whitespace=True, priority=5)


@pendents.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "" or Config.jx3.api.enable:
        return
    await pendents.finish(await pendant(name=args.extract_plain_text()))