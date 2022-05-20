from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from .jx3 import *

horse = on_command("jx3_horse",priority=5)
@horse.handle()
async def _(args: Message = CommandArg()):
    await horse.finish(await horse_flush_place(args.extract_plain_text()))

server = on_command("jx3_server",priority=5)
@server.handle()
async def _(args: Message = CommandArg()):
    await server.finish(await server_status(args.extract_plain_text()))
