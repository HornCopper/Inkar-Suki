from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.const.prompts import PROMPT
from src.const.jx3.server import Server

from .api import get_horse_reporter, get_horse_next_spawn
from .dilu import get_dilu_data

HorseChatMatcher = on_command("jx3_horse_v1", aliases={"抓马v1", "马场v1"}, force_whitespace=True, priority=5)

@HorseChatMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = Server(args.extract_plain_text(), event.group_id).server
    if server is None:
        await HorseChatMatcher.finish(PROMPT.ServerNotExist)
    msg = await get_horse_reporter(server)
    await HorseChatMatcher.finish(msg)

HorseSpawnMatcher = on_command("jx3_horse_v2", aliases={"抓马", "马场"}, force_whitespace=True, priority=5)

@HorseSpawnMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = Server(args.extract_plain_text(), event.group_id).server
    if server is None:
        await HorseSpawnMatcher.finish(PROMPT.ServerNotExist)
    msg = await get_horse_next_spawn(server)
    await HorseSpawnMatcher.finish(msg)

DiluMatcher = on_command("jx3_dilu", aliases={"的卢统计"}, force_whitespace=True, priority=5)

@DiluMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    img = await get_dilu_data()
    if not isinstance(img, str):
        return
    await DiluMatcher.finish(ms.image(img))