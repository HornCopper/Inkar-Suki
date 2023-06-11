from src.tools.dep.bot import *
from .api import *
jx3_cmd_recruit = on_command("jx3_recruit", aliases={"招募"}, priority=5)
@jx3_cmd_recruit.handle()
async def jx3_recruit(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取招募：

    Example：-招募 幽月轮
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text()
    if arg == "":
        if group_server == False:
            await jx3_cmd_recruit.finish("尚未绑定服务器，请携带服务器参数使用！")
        data = await recruit_(server = group_server)
    else:
        arg = arg.split(" ")
        if len(arg) not in [1,2]:
            await jx3_cmd_recruit.finish("参数不正确哦，只能有1或2个参数~")
        if len(arg) == 1:
            if server_mapping(arg[0]) != False or group_server == False:
                server = server_mapping(arg[0], str(event.group_id))
                copy = ""
            else:
                server = getGroupServer(str(event.group_id))
                copy = arg[0]
            data = await recruit_(server, copy)
        else:
            server = server_mapping(arg[0], str(event.group_id))
            copy = arg[1]
            data = await recruit_(server, copy)
    if type(data) == type([]):
        await jx3_cmd_recruit.finish(data[0])
    await jx3_cmd_recruit.finish(ms.image(data))