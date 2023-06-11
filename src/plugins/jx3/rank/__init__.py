from src.tools.dep.bot import *
from .api import *

top100_ = on_command("jx3_top100", aliases={"百强"}, priority=5)
@top100_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取魔盒百强列表：

    Example：-百强 幽月轮 李重茂
    Example：-百强 幽月轮 李重茂 风波渡
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1,2,3]:
        await top100_.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        if group_server == False:
            await top100_.finish("没有绑定服务器，请携带服务器参数使用！")
        server = group_server
        boss = arg[0]
        team = None
    if len(arg) == 2:
        if server_mapping(arg[0]) != False:
            server = arg[0]
            boss = arg[1]
            team = None
        else:
            server = group_server
            if group_server == False:
                await top100_.finish("没有绑定服务器，请携带服务器参数使用！")
            boss = arg[0]
            team = arg[1]
    else:
        server = arg[0]
        boss = arg[1]
        team = arg[2]
    data = await get_top100(server, boss, team)
    await top100_.finish(data)

rank = on_command("jx3_rank", aliases={"榜单"}, priority=5)
@rank.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取风云榜单：

    Example：-榜单 个人 幽月轮 名士五十强
    Example：-榜单 帮会 幽月轮 恶人神兵宝甲五十强
    Example：-榜单 阵营 幽月轮 赛季恶人五十强
    Example：-榜单 试炼 幽月轮 明教
    '''
    group_server = getGroupServer(str(event.group_id))
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [2,3]:
        await rank.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 2:
        if group_server == False:
            await rank.finish("没有绑定服务器，请携带服务器参数使用！")
        type1 = arg[0]
        server = group_server
        type2 = arg[1]
    else:
        type1 = arg[0]
        server = arg[1]
        type2 = arg[1]
    data = await rank_(type_1=type1, server=server, type_2=type2)
    if type(data) == type([]):
        await rank.finish(data[0])
    else:
        await rank.finish(ms.image(data))