from .api import *

firework = on_command("jx3_firework_v2", aliases={"烟花v2"}, priority=5)
@firework.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await firework.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server == False:
            await firework.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    data = await get_firework_image(server, name)
    if type(data) == type([]):
        await firework.finish(data[0])
    else:
        await firework.finish(ms.image(data))