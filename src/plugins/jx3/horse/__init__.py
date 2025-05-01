from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.const.prompts import PROMPT
from src.const.jx3.server import Server

from .api import get_horse_reporter, get_horse_next_spawn

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