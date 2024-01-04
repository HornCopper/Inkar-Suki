from .api import *

jx3_cmd_addritube = on_command(
    "jx3_addritube",
    name="属性v1",
    aliases={'查装v1'},
    priority=5,
    catalog='jx3.pvp.user.property@v1',
    description="查询玩家角色的装备和属性",
    example=[
        Jx3Arg(Jx3ArgsType.server),
        Jx3Arg(Jx3ArgsType.user),
    ],
    document='''''',
)


@jx3_cmd_addritube.handle()
async def jx3_addritube(event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    """
    查询某玩家的装备：

    Example：-属性 幽月轮 哭包猫@唯我独尊
    Example：-查装 幽月轮 哭包猫@唯我独尊
    """
    arg_server, arg_user = template
    data = await addritube_(arg_server, arg_user, group_id=event.group_id)
    if type(data) == type([]):
        return await jx3_cmd_addritube.finish(data[0])
    print(data)
    return await jx3_cmd_addritube.send(ms.image(data))

jx3_cmd_addritube_v2 = on_command(
    "jx3_addritube_v2",
    name="属性",
    aliases={'查装'},
    priority=5,
    catalog='jx3.pvp.user.property@v2',
    description="查询玩家角色的装备和属性",
    example=[
        Jx3Arg(Jx3ArgsType.server),
        Jx3Arg(Jx3ArgsType.user),
    ],
    document='''''',

)


@jx3_cmd_addritube_v2.handle()
async def jx3_addritube_v2(event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_server, arg_user = template
    data = await get_attr_main(arg_server, arg_user, str(event.group_id))
    if type(data) == type([]):
        return await jx3_cmd_addritube_v2.finish(data[0])
    return await jx3_cmd_addritube_v2.send(ms.image(data))

jx3_cmd_roleInfo = on_command("jx3_player", aliases={"玩家信息"}, priority=5)


@jx3_cmd_roleInfo.handle()
async def jx3_player(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取玩家信息：

    Example：-玩家信息 幽月轮 哭包猫@唯我独尊
    """
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(Jx3ArgsType.default)]
    [arg_server, arg_user] = get_args(args, template, event)
    if not arg_server:
        arg_server = server_mapping(group_id=event.group_id)
    msg = await roleInfo_(server=arg_server, player=arg_user)
    await jx3_cmd_roleInfo.finish(msg)
