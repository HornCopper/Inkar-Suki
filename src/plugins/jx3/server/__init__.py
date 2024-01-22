from .api import *

cmd_jx3_server = on_command(
    "jx3_server",
    aliases={"服务器", "开服", '倒闭'},
    description='获取最近的开服状态',
    priority=5,
    catalog=permission.jx3.common.event,
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=True),
    ],
    document='''
    获取服务器开服状态：

    Example：-服务器 幽月轮
    Example：-开服 幽月轮 
    '''
)


@cmd_jx3_server.handle()
async def jx3_server(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_server, = args
    msg = await server_status(server=arg_server)
    return await cmd_jx3_server.finish(msg)
