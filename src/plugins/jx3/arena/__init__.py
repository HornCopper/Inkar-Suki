from src.tools.dep.bot import *
from .api import *

arena = on_command("jx3_arena", aliases={"名剑"}, priority=5)
@arena.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [2,3]:
        await arena.finish("唔……参数数量有误，请检查后重试~")
    group_server = getGroupServer(str(event.group_id))
    if arg[0] == "战绩":
        if len(arg) not in [2,3]:
            await arena.finish("唔……参数数量有误，请检查后重试~")
        if len(arg) == 2:
            if group_server == False:
                await arena.finish("没有绑定服务器，请携带服务器参数使用！")
            server = group_server
            name = arg[1]
        else:
            server = arg[1]
            name = arg[2]
        data = await arena_(object = "战绩", server = server, name = name)
        if type(data) == type([]):
            await arena.finish(data[0])
        else:
            await arena.finish(ms.image(data))
    elif arg[0] == "排行":
        if len(arg) != 2:
            await arena.finish("唔……参数数量有误，请检查后重试~")
        data = await arena_(object = "排行", mode = arg[1])
        if type(data) == type([]):
            await arena.finish(data[0])
        else:
            await arena.finish(ms.image(data))
    elif arg[0] == "统计":
        if len(arg) != 2:
            await arena.finish("唔……参数数量有误，请检查后重试~")
        data = await arena_(object = "统计", mode = arg[1])
        if type(data) == type([]):
            await arena.finish(data[0])
        else:
            await arena.finish(ms.image(data))
