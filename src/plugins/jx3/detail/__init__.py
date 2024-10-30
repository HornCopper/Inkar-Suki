from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.network import Request

from .detail import (
    get_zone_detail_image,
    get_zone_overview_image
)

ZoneOverviewMatcher = on_command("jx3_zone_detail", aliases={"副本总览"}, force_whitespace=True, priority=5)

@ZoneOverviewMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await ZoneOverviewMatcher.finish(PROMPT.ArgumentCountInvalid)
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    serverInstance = Server(server, event.group_id)
    if not serverInstance.server:
        await ZoneOverviewMatcher.finish(PROMPT.ServerNotExist)
    data = await get_zone_overview_image(serverInstance.server, id)
    if isinstance(data, list):
        await ZoneOverviewMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await ZoneOverviewMatcher.finish(ms.image(data))

TeamZoneOverviewMatcher = on_command("jx3_teamoverview", aliases={"团本总览"}, force_whitespace=True, priority=5)

@TeamZoneOverviewMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await TeamZoneOverviewMatcher.finish(PROMPT.ArgumentCountInvalid)
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    serverInstance = Server(server, event.group_id)
    if not serverInstance.server:
        await TeamZoneOverviewMatcher.finish(PROMPT.ServerNotExist)
    data = await get_zone_detail_image(serverInstance.server, id, True)
    if isinstance(data, list):
        await TeamZoneOverviewMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await TeamZoneOverviewMatcher.finish(ms.image(data))

FiveZoneOverviewMatcher = on_command("jx3_5overview", aliases={"五人总览"}, force_whitespace=True, priority=5)

@FiveZoneOverviewMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await FiveZoneOverviewMatcher.finish(PROMPT.ArgumentCountInvalid)
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    serverInstance = Server(server, event.group_id)
    if not serverInstance.server:
        await FiveZoneOverviewMatcher.finish(PROMPT.ServerNotExist)
    data = await get_zone_detail_image(serverInstance.server, id, False)
    if isinstance(data, list):
        await FiveZoneOverviewMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await FiveZoneOverviewMatcher.finish(ms.image(data))