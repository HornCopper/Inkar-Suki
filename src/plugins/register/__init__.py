import json, sys, nonebot
from nonebot import on_command, on_message
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
from permission import checker, error
from file import read, write

unregistered = on_message(block=False)
@unregistered.handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    pass
