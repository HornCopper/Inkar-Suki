from src.tools.dep.bot import *
from .api import *

serendipity = on_command("jx3_serendipity", aliases={"奇遇"}, priority=5)
@serendipity.handle()  
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取个人奇遇记录：

    Example：-奇遇 幽月轮 哭包猫@唯我独尊
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await serendipity.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server == False:
            await serendipity.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        id = arg[0]
    elif len(arg) ==2:
        server = arg[0]
        id = arg[1]
    data = await serendipity_(server, id)
    if type(data) == type([]):
        await serendipity.finish(data[0])
    else:
        await serendipity.finish(ms.image(data))

statistical = on_command("jx3_lstatistical", aliases={"近期奇遇"}, priority=5)
@statistical.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取某服务器最近出奇遇的人的列表：

    Example：-近期奇遇 幽月轮 阴阳两界
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await statistical.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server == False:
            await statistical.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        name = arg[0]
    elif len(arg) ==2:
        server = arg[0]
        name = arg[1]
    data = await statistical_(server, serendipity = name)
    if type(data) == type([]):
        await statistical.finish(data[0])
    else:
        await statistical.finish(ms.image(data))

gserendipity = on_command("jx3_gserendipity", aliases={"全服奇遇"}, priority=5)
@gserendipity.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取全服最近某奇遇的触发列表，按触发顺序：

    Example：-全服奇遇 阴阳两界
    '''
    arg = args.extract_plain_text()
    if arg == "":
        await gserendipity.finish("唔，缺少奇遇名称，没有办法找哦~")
    data = await global_serendipity(arg)
    if type(data) == type([]):
        await gserendipity.finish(data[0])
    else:
        await gserendipity.finish(ms.image(data))

gstatistical = on_command("jx3_gstatistical", aliases={"全服统计"}, priority=5)
@gstatistical.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取各服奇遇的触发者，统计图表：

    Example：-全服统计 阴阳两界
    '''
    arg = args.extract_plain_text()
    if arg == "":
        await gstatistical.finish("唔，缺少奇遇名称，没有办法找哦~")
    data = await global_statistical(arg)
    if type(data) == type([]):
        await gstatistical.finish(data[0])
    else:
        await gstatistical.finish(ms.image(data))
