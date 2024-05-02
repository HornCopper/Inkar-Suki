from .api import *
from .monster import *

zones = on_command("jx3_zones_v1", aliases={"副本v1"}, force_whitespace=True, priority=5)


@zones.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取玩家副本通关记录：

    Example：-副本v1 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await zones.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server is False:
            await zones.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await zone(server, id)
    if isinstance(data, list):
        await zones.finish(data[0])
    data = await get_content(data)
    await zones.finish(ms.image(data))

zonesv2 = on_command("jx3_zones", aliases={"副本"}, force_whitespace=True, priority=5)


@zonesv2.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await zonesv2.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server is False:
            await zonesv2.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await zone_v2(server, id)
    if isinstance(data, list):
        await zonesv2.finish(data[0])
    data = get_content_local(data)
    await zonesv2.finish(ms.image(data))

drops = on_command("jx3_drops", aliases={"掉落列表"}, force_whitespace=True, priority=5)


@drops.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 3:
        await drops.finish("唔……参数不正确哦~")
    map = arg[0]
    mode = arg[1]
    boss = arg[2]
    data = await generater(map, mode, boss)
    from nonebot.log import logger
    logger.info(data)
    if not isinstance(data, list):
        data = get_content_local(data)
        await drops.send(ms.image(data))
    await drops.finish(data[0])

item = on_command("jx3_itemdrop", aliases={"掉落"}, force_whitespace=True, priority=5)


@item.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await item.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server is False:
            await item.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    data = await get_item_record(server, name)
    if isinstance(data, list):
        await item.finish(data[0])
    data = get_content_local(data)
    await item.finish(ms.image(data))

monsters = on_command("jx3_monsters_v2", aliases={"百战v2"}, force_whitespace=True, priority=5)

@monsters.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    img = await get_monsters_map()
    await monsters.finish(ms.image(img))