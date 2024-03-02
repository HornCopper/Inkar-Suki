from .api import *
jx3_cmd_addritube_v2 = on_command(
    "jx3_addritube_v2",
    name="属性v2",
    aliases={'查装v2'},
    priority=5,
    catalog=permission.jx3.pvp.user.attribute,
    description="查询玩家角色的装备和属性",
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=True),
        Jx3Arg(Jx3ArgsType.user),
    ],
    document="""""",

)


@jx3_cmd_addritube_v2.handle()
async def jx3_addritube_v2(event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_server, arg_user = template
    if not arg_server:
        await jx3_cmd_addritube_v2.finish(PROMPT_ServerNotExist)
    data = await get_attr_main(arg_server, arg_user, str(event.group_id))
    if isinstance(data, list):
        await jx3_cmd_addritube_v2.finish(data[0])
    await jx3_cmd_addritube_v2.send(ms.image(data))

jx3_cmd_roleInfo = on_command(
    "玩家信息",
    aliases={"玩家"},
    priority=5,
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=True),
        Jx3Arg(Jx3ArgsType.user),
    ]
)


@jx3_cmd_roleInfo.handle()
async def jx3_roleInfo(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    """
    获取玩家信息：

    Example：-玩家信息 幽月轮 哭包猫@唯我独尊
    """
    arg_server, arg_user = args
    if not arg_server:
        await jx3_cmd_roleInfo.finish(PROMPT_ServerNotExist)
    msg = await roleInfo_(server=arg_server, player=arg_user)
    await jx3_cmd_roleInfo.send(msg)
