from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment as ms

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.network import Request

from .api import get_arena_record

ArenaRecordMatcher = on_command("jx3_arena_record", aliases={"战绩"}, force_whitespace=True, priority=5)

@ArenaRecordMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await ArenaRecordMatcher.finish(PROMPT.ArgumentCountInvalid)
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await ArenaRecordMatcher.finish(PROMPT.ServerNotExist)
    data = await get_arena_record(server, name)
    if isinstance(data, list):
        await ArenaRecordMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await ArenaRecordMatcher.finish(ms.image(data))