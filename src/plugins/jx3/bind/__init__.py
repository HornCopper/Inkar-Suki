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
    path = f"{bot_path.DATA}/{group_id}/jx3group.json"
    now = json.loads(read(path))
    now["server"] = server
    write(path, json.dumps(now, ensure_ascii=False))
    return server


jx3_cmd_server_bind = on_command(
    "绑定",
    aliases={},
    priority=5,
    example=[
        Jx3Arg(Jx3ArgsType.server, is_optional=False)
    ]
)


@jx3_cmd_server_bind.handle()
async def jx3_server_bind(bot: Bot, event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    # TODO 判别权限，应提取为专有函数
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        x = Permission(event.user_id).judge(8, '绑定服务器')
        if not x.success:
            return await jx3_cmd_server_bind.finish("唔……只有群主或管理员才可以修改哦！")

    server, = args
    server = server_bind(group_id=event.group_id, server=server)
    if isinstance(server, list):
        return await jx3_cmd_server_bind.finish(f"绑定失败：{server}")
    return await jx3_cmd_server_bind.finish("绑定成功！\n当前区服为：" + server)

jx3_cmd_server_unbind = on_command("jx3_unbind", aliases={"解绑"}, priority=5)


@jx3_cmd_server_unbind.handle()
async def jx3_server_bind(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # TODO 判别权限，应提取为专有函数
    personal_data = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=event.user_id, no_cache=True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    if not group_admin:
        x = Permission(event.user_id).judge(8, '解绑服务器')
        if not x.success:
            return await jx3_cmd_server_unbind.finish("唔……只有群主或管理员才可以修改哦！")

    server_bind(group_id=event.group_id, server=None)
    return await jx3_cmd_server_unbind.finish("已解绑")
