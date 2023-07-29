from .api import *

jx3_cmd_recruit = on_command("jx3_recruit", aliases={"招募"}, priority=5)

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
    if type(data) == type([]):
        await jx3_cmd_recruit.finish(data[0])
    await jx3_cmd_recruit.finish(ms.image(data))

recruitv2 = on_command("jx3_recruit_v2", aliases={"招募v2"}, priority=5)

@recruitv2.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text()
    if arg == "":
        group_server = getGroupServer(str(event.group_id))
        if not group_server:
            await recruitv2.finish("尚未绑定服务器，请携带服务器参数使用！")
        data = await recruit_v2(group_server)
    else:
        arg = arg.split(" ")
        if len(arg) not in [1, 2]:
            await recruitv2.finish("参数不正确哦，只能有1或2个参数~")
        server = server_mapping(arg[0], str(event.group_id))
        if len(arg) == 1:
            copy = arg[0] if not server_mapping(arg[0]) else ""  # 当第一个参数是服务器的话则为空
        else:
            copy = arg[1]
        data = await recruit_v2(server, copy)
    if type(data) == type([]):
        await recruitv2.finish(data[0])
    await recruitv2.finish(ms.image(data))