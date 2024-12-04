from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent

from src.const.prompts import PROMPT
from src.const.jx3.server import Server

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
    await ArenaRecordMatcher.finish(data)