from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.const.jx3.dungeon import Dungeon
from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.network import Request

from .api import (
    get_zone_record_image,
    get_drop_list_image
)
from .monster import get_monsters_map

ZoneRecordMatcher = on_command("jx3_zones", aliases={"副本"}, force_whitespace=True, priority=5)


@ZoneRecordMatcher.handle()
async def _(event: GroupMessageEvent, full_argument: Message = CommandArg()):
    if full_argument.extract_plain_text() == "":
        return
    args = full_argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await ZoneRecordMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(args) == 1:
        server = None
        name = args[0]
    elif len(args) == 2:
        server = args[0]
        name = args[1]
    server = Server(server, event.group_id).server
    if server is None:
        await ZoneRecordMatcher.finish(PROMPT.ServerNotExist)
    data = await get_zone_record_image(server, name)
    if isinstance(data, list):
        await ZoneRecordMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await ZoneRecordMatcher.finish(ms.image(data))

DropsListMatcher = on_command("jx3_drops", aliases={"掉落列表"}, force_whitespace=True, priority=5)


@DropsListMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 3:
        await DropsListMatcher.finish("唔……参数不正确哦~")
    map = arg[0]
    mode = arg[1]
    boss = arg[2]
    dungeonInstance = Dungeon(map, mode)
    if dungeonInstance.name is None or dungeonInstance.mode is None:
        await DropsListMatcher.finish(PROMPT.DungeonInvalid)
    data = await get_drop_list_image(dungeonInstance.name, dungeonInstance.mode, boss)
    if isinstance(data, str):
        data = Request(data).local_content
        await DropsListMatcher.send(ms.image(data))
    elif isinstance(data, list):
        await DropsListMatcher.finish(data[0])

MonstersMatcher = on_command("jx3_monsters_v2", aliases={"百战v2", "百战"}, force_whitespace=True, priority=5)

@MonstersMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    img = await get_monsters_map()
    if isinstance(img, str):
        await MonstersMatcher.finish(ms.image(Request(img).local_content))