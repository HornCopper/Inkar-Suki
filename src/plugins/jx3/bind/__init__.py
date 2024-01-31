from src.tools.permission import checker

from .api import *


def server_bind(group_id: str, server: str) -> str:
    """
    绑定输入项为有效服务器，并返回该服务器名称
    @group_id:str:群号
    @server:str:服务器名
    """
    # 当server为None表示要清空，否则检查服务器名称有效性
    if server:
        server = server_mapping(server)
        if not server:
            return [PROMPT_ServerNotExist]
    group_config = GroupConfig(group_id)
    _ = group_config.mgr_property("server", server)
    return server


jx3_cmd_server_bind = on_command(
    "绑定",
    aliases={"绑定服务器", "绑定区服", "注册", "绑"},
    priority=5,
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=False)
    ]
)


@jx3_cmd_server_bind.handle()
async def jx3_server_bind(bot: Bot, event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        if checker(str(event.user_id), 5) == False:
            await jx3_cmd_server_bind.finish(error(5))
    arg_server, = args
    if not arg_server:
        return await jx3_cmd_server_bind.finish(PROMPT_ServerNotExist)

    arg_server = server_bind(group_id=event.group_id, server=arg_server)
    if isinstance(arg_server, list):
        return await jx3_cmd_server_bind.finish(f"绑定失败：{arg_server}")
    return await jx3_cmd_server_bind.finish("绑定成功！\n当前区服为：" + arg_server)

jx3_cmd_server_unbind = on_command("jx3_unbind", aliases={"解绑"}, priority=5)


@jx3_cmd_server_unbind.handle()
async def jx3_server_bind(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        if checker(str(event.user_id), 8) == False:
            await jx3_cmd_server_unbind.finish(error(8))

    server_bind(group_id=event.group_id, server=None)
    return await jx3_cmd_server_unbind.finish("好的！已将本群的服务器绑定清空~\n如需再次绑定，请发送“绑定 服务器”。")
