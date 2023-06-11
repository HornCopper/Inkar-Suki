from src.tools.dep.bot import *
from .api import *

addritube = on_command("jx3_addritube", aliases={"属性","查装"}, priority=5)
@addritube.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    查询某玩家的装备：

    Example：-属性 幽月轮 哭包猫@唯我独尊
    Example：-查装 幽月轮 哭包猫@唯我独尊
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await addritube.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server == False:
            await addritube.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        id = arg[0]
    elif len(arg) ==2:
        server = arg[0]
        id = arg[1]
    data = await addritube_(server, id)
    if type(data) == type([]):
        await addritube.finish(data[0])
    else:
        await addritube.finish(ms.image(data))


roleInfo = on_command("jx3_player", aliases={"玩家信息"}, priority=5)
@roleInfo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取玩家信息：

    Example：-玩家信息 幽月轮 哭包猫@唯我独尊
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2]:
        await roleInfo.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server == False:
            await roleInfo.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        id = arg[0]
    elif len(arg) ==2:
        server = arg[0]
        id = arg[1]
    msg = await roleInfo_(server = server, player = id)
    await roleInfo.finish(msg)