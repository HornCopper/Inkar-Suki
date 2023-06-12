from src.tools.dep.bot import *
from .api import *

firework__ = on_command("jx3-firework", aliases={"_烟花"}, priority=5)
@firework__.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    group_server = getGroupServer(str(event.group_id))
    from src.plugins.jx3.firework import get_data as firework_ # CodeThink独家出品，仅限公共音卡使用，闭源
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await firework__.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server == False:
            await firework__.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        name = arg[0]
    elif len(arg) ==2:
        server = arg[0]
        name = arg[1]
    img = await firework_(server, name)
    if type(img) == type([]):
        await firework__.finish(img[0])
    else:
        await firework__.finish(img)