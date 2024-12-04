from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.utils.network import Request

from .koromo import find_player, get_records, player_pt

MSSearchPlayerMatcher = on_command("search_player", aliases={"mssp"}, priority=5, force_whitespace=True)

@MSSearchPlayerMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    data = await find_player(args.extract_plain_text())
    await MSSearchPlayerMatcher.finish(data)


MSGameRecordMatcher = on_command("get_records", aliases={"msgr"}, priority=5, force_whitespace=True)

@MSGameRecordMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    data = await get_records(args.extract_plain_text())
    await MSGameRecordMatcher.finish(data)


MSGetPTMatcher = on_command("get_pt", aliases={"mspt"}, priority=5, force_whitespace=True)

@MSGetPTMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    data = await player_pt(args.extract_plain_text())
    await MSGetPTMatcher.finish(data)