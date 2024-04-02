from .api import *

jx3_cmd_addritube = on_command("jx3_addritube", aliases={"属性v1", "查装v1"}, priority=5)


@jx3_cmd_addritube.handle()
async def jx3_addritube(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询某玩家的装备：

    Example：-属性 幽月轮 哭包猫@唯我独尊
    Example：-查装 幽月轮 哭包猫@唯我独尊
    """
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await jx3_cmd_addritube.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await addritube_(server, id, group_id=event.group_id)
    if type(data) == type([]):
        await jx3_cmd_addritube.finish(data[0])
    else:
        data = await get_content(data)
        await jx3_cmd_addritube.finish(ms.image(data))

jx3_cmd_addritube_v2 = on_command("jx3_addritube_v2", aliases={"属性", "查装", "属性v2", "查装v2"}, priority=5)


@jx3_cmd_addritube_v2.handle()
async def jx3_addritube(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询某玩家的装备：

    Example：-属性 幽月轮 哭包猫@唯我独尊
    Example：-查装 幽月轮 哭包猫@唯我独尊
    """
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await jx3_cmd_addritube_v2.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await get_attr_main(server, id, str(event.group_id))
    if type(data) == type([]):
        await jx3_cmd_addritube_v2.finish(data[0])
    else:
        data = get_content_local(data)
        await jx3_cmd_addritube_v2.finish(ms.image(data))

jx3_cmd_roleInfo = on_command("jx3_player", aliases={"玩家信息"}, priority=5)


@jx3_cmd_roleInfo.handle()
async def jx3_player(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取玩家信息：

    Example：-玩家信息 幽月轮 哭包猫@唯我独尊
    """
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await jx3_cmd_roleInfo.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    msg = await roleInfo_(server=server, player=id, group_id=event.group_id)
    await jx3_cmd_roleInfo.finish(msg)