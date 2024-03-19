from .api import *

jx3_cmd_recruit = on_command("jx3_recruit_v1", aliases={"招募v1"}, priority=5)


@jx3_cmd_recruit.handle()
async def jx3_recruit(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取招募：

    Example：-招募 幽月轮
    """
    arg = args.extract_plain_text()
    if arg == "":
        group_server = getGroupServer(str(event.group_id))
        if not group_server:
            await jx3_cmd_recruit.finish("尚未绑定服务器，请携带服务器参数使用！")
        data = await api_recruit(server=group_server)
    else:
        arg = arg.split(" ")
        if len(arg) not in [1, 2]:
            await jx3_cmd_recruit.finish("参数不正确哦，只能有1或2个参数~")
        server = server_mapping(arg[0], str(event.group_id))
        if len(arg) == 1:
            copy = arg[0] if not server_mapping(arg[0]) else ""  # 当第一个参数是服务器的话则为空
        else:
            copy = arg[1]
        data = await api_recruit(server, copy)
    if isinstance(data, list):
        await jx3_cmd_recruit.finish(data[0])
    data = await get_content(data)
    await jx3_cmd_recruit.send(ms.image(data))

jx3_cmd_recruit_v2 = on_command("jx3_recruit", aliases={"招募"}, priority=5)


@jx3_cmd_recruit_v2.handle()
async def jx3_recruit_v2(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text()
    if arg == "":
        group_server = getGroupServer(str(event.group_id))
        if not group_server:
            await jx3_cmd_recruit_v2.finish("尚未绑定服务器，请携带服务器参数使用！")
        data = await recruit_v2(group_server)
    else:
        arg = arg.split(" ")
        if len(arg) not in [1, 2]:
            await jx3_cmd_recruit_v2.finish("参数不正确哦，只能有1或2个参数~")
        server = server_mapping(arg[0], str(event.group_id))
        if len(arg) == 1:
            copy = arg[0] if not server_mapping(arg[0]) else ""  # 当第一个参数是服务器的话则为空
        else:
            copy = arg[1]
        data = await recruit_v2(server, copy, local=False)
    if isinstance(data, list):
        await jx3_cmd_recruit_v2.finish(data[0])
    data = get_content_local(data)
    await jx3_cmd_recruit_v2.finish(ms.image(data))


jx3_cmd_recruit_local = on_command("jx3_recruit_local", aliases={"本服招募"}, priority=5)


@jx3_cmd_recruit_local.handle()
async def jx3_recruit_v2(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text()
    if arg == "":
        group_server = getGroupServer(str(event.group_id))
        if not group_server:
            await jx3_cmd_recruit_local.finish("尚未绑定服务器，请携带服务器参数使用！")
        data = await recruit_v2(group_server, local=True)
    else:
        arg = arg.split(" ")
        if len(arg) not in [1, 2]:
            await jx3_cmd_recruit_local.finish("参数不正确哦，只能有1或2个参数~")
        server = server_mapping(arg[0], str(event.group_id))
        if len(arg) == 1:
            copy = arg[0] if not server_mapping(arg[0]) else ""  # 当第一个参数是服务器的话则为空
        else:
            copy = arg[1]
        data = await recruit_v2(server, copy, local=True)
    if isinstance(data, list):
        await jx3_cmd_recruit_local.finish(data[0])
    data = get_content_local(data)
    await jx3_cmd_recruit_local.finish(ms.image(data))
