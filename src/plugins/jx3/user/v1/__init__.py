from .api import *
jx3_cmd_addritube = on_command(
    "jx3_addritube",
    name="属性v1",
    aliases={"查装v1"},
    priority=5,
    catalog=permission.jx3.pvp.user.attribute,
    description="查询玩家角色的装备和属性",
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=True),
        Jx3Arg(Jx3ArgsType.user),
    ],
    document="""""",
)


@jx3_cmd_addritube.handle()
async def jx3_addritube(event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    """
    查询某玩家的装备：

    Example：-属性 幽月轮 哭包猫@唯我独尊
    Example：-查装 幽月轮 哭包猫@唯我独尊
    """
    arg_server, arg_user = template
    if not arg_server:
        await jx3_cmd_addritube.finish(PROMPT_ServerNotExist)
    data = await addritube_(arg_server, arg_user)
    if isinstance(data, list):
        await jx3_cmd_addritube.finish(data[0])
    await jx3_cmd_addritube.send(ms.image(data))
