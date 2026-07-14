from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.const.prompts import PROMPT
from src.const.jx3.server import Server

from .api import get_horse_reporter, get_horse_next_spawn
from .dilu import get_dilu_records


dilu_matcher = on_command(
    "jx3_dilu",
    aliases={"的卢统计"},
    force_whitespace=True,
    priority=5,
)


@dilu_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    argument = args.extract_plain_text().strip()
    if argument:
        if argument == "全服":
            server = ""
        else:
            server = Server(argument).server
            if server is None:
                await dilu_matcher.finish(PROMPT.ServerNotExist)
    else:
        server = Server(None, event.group_id).server
        if server is None:
            await dilu_matcher.finish(PROMPT.ServerNotExist)
    image = await get_dilu_records(server)
    await dilu_matcher.finish(image)

horse_chat_matcher = on_command("jx3_horse_v1", aliases={"抓马v1", "马场v1"}, force_whitespace=True, priority=5)

@horse_chat_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = Server(args.extract_plain_text(), event.group_id).server
    if server is None:
        await horse_chat_matcher.finish(PROMPT.ServerNotExist)
    msg = await get_horse_reporter(server)
    await horse_chat_matcher.finish(msg)

horse_spawn_matcher = on_command("jx3_horse_v2", aliases={"抓马", "马场"}, force_whitespace=True, priority=5)

@horse_spawn_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = Server(args.extract_plain_text(), event.group_id).server
    if server is None:
        await horse_spawn_matcher.finish(PROMPT.ServerNotExist)
    msg = await get_horse_next_spawn(server)
    await horse_spawn_matcher.finish(msg)
