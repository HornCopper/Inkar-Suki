from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

from src.config import Config
from src.const.jx3.dungeon import Dungeon
from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.permission import check_permission
from src.utils.database.operation import get_group_settings

from .zone_drop import get_drop_list_image
# from .monster import get_monsters_map
from .record import get_item_record
from .teamcd import get_zone_record_image, get_mulit_record_image, get_personal_roles_teamcd_image

ZoneRecordMatcher = on_command("jx3_zones", aliases={"副本"}, force_whitespace=True, priority=5)

@ZoneRecordMatcher.handle()
async def _(event: GroupMessageEvent, message: Message = CommandArg()):
    if message.extract_plain_text() == "":
        return
    args = message.extract_plain_text().strip().split(" ")
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
    if name == "*":
        await ZoneRecordMatcher.send("提示：“副本 *”用法将在4月17日新赛季开启后停止使用。\n请移步“副本列表”命令。\n用法：副本列表 [副本名(可留空)]")
        data = await get_personal_roles_teamcd_image(event.user_id)
    elif ";" in name:
        roles = name.split(";")
        if len(roles) > 6 and not check_permission(event.user_id, 6):
            await ZoneRecordMatcher.finish("最多一次只可以查询6个角色！")
        data = await get_mulit_record_image(server, roles)
    else:
        data = await get_zone_record_image(server, name)
    await ZoneRecordMatcher.finish(data)

AllRolesTeamcdMatcher = on_command("jx3_zoneslist", aliases={"副本列表"}, force_whitespace=True, priority=5)

@AllRolesTeamcdMatcher.handle()
async def _(event: GroupMessageEvent, message: Message = CommandArg()):
    msg = message.extract_plain_text().strip()
    image = await get_personal_roles_teamcd_image(event.user_id, msg)
    await AllRolesTeamcdMatcher.finish(image)

DropslistMatcher = on_command("jx3_drops", aliases={"掉落列表"}, force_whitespace=True, priority=5)

@DropslistMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 3:
        await DropslistMatcher.finish("唔……参数不正确哦~")
    map = arg[0]
    mode = arg[1]
    boss = arg[2]
    dungeonInstance = Dungeon(map, mode)
    if dungeonInstance.name is None or dungeonInstance.mode is None:
        await DropslistMatcher.finish(PROMPT.DungeonInvalid)
    data = await get_drop_list_image(dungeonInstance.name, dungeonInstance.mode, boss)
    await DropslistMatcher.finish(data)

MonstersMatcher = on_command("jx3_monsters_v2", aliases={"百战v2", "百战"}, force_whitespace=True, priority=5)

@MonstersMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    from .monster import get_monsters_map
    img = await get_monsters_map()
    await MonstersMatcher.finish(img)

AllServerItemRecordMatcher = on_command("jx3_itemrecord_allserver", aliases={"全服掉落"}, force_whitespace=True, priority=5)

@AllServerItemRecordMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    additions = get_group_settings(str(event.group_id), "additions")
    if not Config.jx3.api.enable and not "Preview" in additions:
        return
    item_name = args.extract_plain_text()
    data = await get_item_record(item_name)
    await AllServerItemRecordMatcher.finish(data)