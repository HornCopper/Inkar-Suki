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
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(Jx3ArgsType.default)]
    arg_server, arg_user = get_args(args.extract_plain_text(), template)
    if not arg_user:
        return await jx3_cmd_addritube.finish(PROMPT_ArgumentCountInvalid)
    arg_server = server_mapping(arg_server, event.group_id)
    data = await addritube_(arg_server, arg_user, group_id=event.group_id)
    if type(data) == type([]):
        await jx3_cmd_addritube.finish(data[0])
    else:
        await jx3_cmd_addritube.finish(ms.image(data))

addritube_v2 = on_command("jx3_addritube_v2", aliases={"属性v2"}, priority=5)


@addritube_v2.handle()
async def jx3_addritube_v2(event: GroupMessageEvent, args: Message = CommandArg()):
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(Jx3ArgsType.default)]
    arg_server, arg_user = get_args(args.extract_plain_text(), template)
    if not arg_user:
        return await jx3_cmd_addritube.finish(PROMPT_ArgumentCountInvalid)
    data = await get_attr_main(arg_server, arg_user)
    if type(data) == type([]):
        await addritube_v2.finish(data[0])
    else:
        await addritube_v2.finish(ms.image(data))

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
    msg = await roleInfo_(server=arg_server, player=arg_user)
    await jx3_cmd_roleInfo.finish(msg)
