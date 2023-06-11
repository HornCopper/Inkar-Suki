from src.tools.dep.bot import *
from .api import *

ct = on_command("jx3_ct", aliases={"赤兔"}, priority=5)
@ct.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取赤兔刷新信息：

    Example：-赤兔 幽月轮
    '''
    group_server = getGroupServer(str(event.group_id))
    server = args.extract_plain_text()
    if server == "":
        if group_server == False:
            await ct.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
    else:
        server = server
    msg = await get_chitu(server)
    await ct.finish(msg)

horse = on_command("jx3_horse", aliases={"抓马","马场"}, priority=5)
@horse.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = args.extract_plain_text()
    group_server = getGroupServer(str(event.group_id))
    if server == "":
        if group_server == False:
            await horse.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
    else:
        server = server
    msg = await get_horse_reporter(server)
    await horse.finish(msg)