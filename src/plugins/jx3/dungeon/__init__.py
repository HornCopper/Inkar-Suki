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
from .record import get_item_record
from .teamcd import get_zone_record_image, get_mulit_record_image, get_personal_roles_teamcd_image
from .role_monster import get_role_monsters_map
from .monster import get_monsters_map

zone_record_matcher = on_command("jx3_zones", aliases={"副本"}, force_whitespace=True, priority=5)

@zone_record_matcher.handle()
async def _(event: GroupMessageEvent, message: Message = CommandArg()):
    if message.extract_plain_text() == "":
        return
    args = message.extract_plain_text().strip().split(" ")
    if len(args) not in [1, 2]:
        await zone_record_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：副本 <服务器> <角色名>\n参考格式：副本 <服务器> <多角色>\n多角色以英文分号(;)分割。")
    if len(args) == 1:
        server = None
        name = args[0]
    elif len(args) == 2:
        server = args[0]
        name = args[1]
    server = Server(server, event.group_id).server
    if server is None:
        await zone_record_matcher.finish(PROMPT.ServerNotExist)
    if name == "*":
        data = await get_personal_roles_teamcd_image(event.user_id)
    elif ";" in name:
        roles = name.split(";")
        if len(roles) > 6 and not check_permission(event.user_id, 6):
            await zone_record_matcher.finish("最多一次只可以查询6个角色！")
        data = await get_mulit_record_image(server, roles)
    else:
        data = await get_zone_record_image(server, name)
    await zone_record_matcher.finish(data)

all_roles_teamcd_matcher = on_command("jx3_zoneslist", aliases={"副本列表"}, force_whitespace=True, priority=5)

@all_roles_teamcd_matcher.handle()
async def _(event: GroupMessageEvent, message: Message = CommandArg()):
    msg = message.extract_plain_text().strip()
    image = await get_personal_roles_teamcd_image(event.user_id, msg)
    await all_roles_teamcd_matcher.finish(image)

drops_list_matcher = on_command("jx3_drops", aliases={"掉落列表"}, force_whitespace=True, priority=5)

@drops_list_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 3:
        await drops_list_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：掉落列表 <副本名> <副本难度> <首领名>")
    map = arg[0]
    mode = arg[1]
    boss = arg[2]
    dungeonInstance = Dungeon(map, mode)
    if dungeonInstance.name is None or dungeonInstance.mode is None:
        await drops_list_matcher.finish(PROMPT.DungeonInvalid)
    data = await get_drop_list_image(dungeonInstance.name, dungeonInstance.mode, boss)
    await drops_list_matcher.finish(data)

monsters_matcher = on_command("jx3_monsters_v2", aliases={"百战v2", "百战"}, force_whitespace=True, priority=5)

@monsters_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    img = await get_monsters_map()
    await monsters_matcher.finish(img)

role_monsters_matcher = on_command("jx3_role_monster", aliases={"精耐"}, force_whitespace=True, priority=5)

@role_monsters_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    additions = get_group_settings(str(event.group_id), "additions")
    if not Config.jx3.api.enable or "Preview" not in additions:
        return
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) not in [1, 2]:
        await role_monsters_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：精耐 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        role_name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        role_name = arg[1]
    server = Server(server, event.group_id).server
    if not server:
        await role_monsters_matcher.finish(PROMPT.ServerNotExist)
    data = await get_role_monsters_map(server, role_name)
    await role_monsters_matcher.finish(data)

allserver_item_record_matcher = on_command("jx3_itemrecord_allserver", aliases={"全服掉落"}, force_whitespace=True, priority=5)

@allserver_item_record_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    additions = get_group_settings(str(event.group_id), "additions")
    if not Config.jx3.api.enable and "Preview" not in additions:
        return
    item_name = args.extract_plain_text()
    data = await get_item_record(item_name)
    await allserver_item_record_matcher.finish(data)