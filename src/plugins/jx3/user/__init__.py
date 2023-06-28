from .api import *

jx3_cmd_addritube = on_command("jx3_addritube", aliases={
                               "属性", "查装"}, priority=5)


@jx3_cmd_addritube.handle()
async def jx3_addritube(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    查询某玩家的装备：

    Example：-属性 幽月轮 哭包猫@唯我独尊
    Example：-查装 幽月轮 哭包猫@唯我独尊
    '''
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
        await jx3_cmd_addritube.finish(ms.image(data))


jx3_cmd_roleInfo = on_command("jx3_player", aliases={"玩家信息"}, priority=5)


@jx3_cmd_roleInfo.handle()
async def jx3_player(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取玩家信息：

    Example：-玩家信息 幽月轮 哭包猫@唯我独尊
    '''
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(Jx3ArgsType.default)]
    [arg_server, arg_user] = get_args(args.extract_plain_text(), template)
    if not arg_server:
        arg_server = server_mapping(group_id=event.group_id)
    msg = await roleInfo_(server=arg_server, player=arg_user, group_id=event.group_id)
    await jx3_cmd_roleInfo.finish(msg)
