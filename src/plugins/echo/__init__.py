import sys
from pathlib import Path

from nonebot.adapters.onebot.v11 import Event
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import on_command

TOOLS = Path(__file__).resolve().parent.parent.parent / "tools"
sys.path.append(str(TOOLS))
from permission import checker, error

from functools import reduce
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    unescape,
)


echo = on_command("echo",priority=5)


@echo.handle()
async def echo_(matcher: Matcher, event: Event, args: Message = CommandArg()):
    if checker(str(event.user_id),9) == False:
        await echo.finish(error(9))
    await echo.finish(args)


say = on_command("say",priority=5)


@say.handle()
async def say_(matcher: Matcher, event: Event, args: Message = CommandArg()): 
    def _unescape(message: Message, segment: MessageSegment):
        if segment.is_text():
            return message.append(unescape(str(segment)))
        return message.append(segment)
    if checker(str(event.user_id),9) == False:
        await say.finish(error(9))
    message = reduce(_unescape, args, Message())
    await say.finish(message)
