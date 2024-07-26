from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.tools.basic.data_server import server_mapping
from src.tools.utils.request import get_content, get_api
from src.tools.config import Config

from .api import *
from .school_rank import *
from .top100 import *

jx3_cmd_top100_ = on_command("jx3_top100", aliases={"百强"}, force_whitespace=True, priority=5)

@jx3_cmd_top100_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取魔盒百强列表：

    Example：-百强 幽月轮 李重茂
    Example：-百强 幽月轮 李重茂 风波渡
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2, 3]:
        await jx3_cmd_top100_.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        boss = arg[0]
        team = None
    elif len(arg) == 2:
        s = server_mapping(arg[0])
        if s:
            server = s
            boss = arg[1]
            team = None
        else:
            server = None
            boss = arg[0]
            team = arg[1]
    else:
        server = server_mapping(arg[0])
        boss = arg[1]
        team = arg[2]
    data = await get_top100(server, boss, team)
    await jx3_cmd_top100_.finish(data)

jx3_cmd_rank = on_command("jx3_rank", aliases={"榜单"}, force_whitespace=True, priority=5)

@jx3_cmd_rank.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取风云榜单：

    Example：-榜单 个人 幽月轮 名士五十强
    Example：-榜单 帮会 幽月轮 恶人神兵宝甲五十强
    Example：-榜单 阵营 幽月轮 赛季恶人五十强
    """
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [2, 3]:
        await jx3_cmd_rank.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 2:
        type1 = arg[0]
        server = None
        type2 = arg[1]
    else:
        type1 = arg[0]
        server = arg[1]
        type2 = arg[2]
    data = await rank_(type_1=type1, server=server, type_2=type2, group_id=event.group_id)
    if isinstance(data, list):
        await jx3_cmd_rank.finish(data[0])
    else:
        data = await get_content(data)
        await jx3_cmd_rank.finish(ms.image(data))

sl_rank = on_command("jx3_slrank", aliases={"试炼"}, force_whitespace=True, priority=5)

@sl_rank.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取试炼榜：
    Example：-试炼 全服 万花
    Example：-试炼 万花
    Example：-试炼 幽月轮 万花
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await sl_rank.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        school = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        school = arg[1]
    img = await sl_rank_(server, str(event.group_id), school)
    if type(img) == type([]):
        await sl_rank.finish(img[0])
    else:
        img = await get_content(img)
        await sl_rank.finish(ms.image(img))

rank = on_command("jx3_schoolrank", aliases={"门派天梯", "天梯"}, force_whitespace=True, priority=5)

@rank.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    season = args.extract_plain_text()
    season_data = await get_api("https://cms.jx3box.com/api/cms/bps/dps/ladder?client=std")
    if season == "":
        season_key = season_data["data"][0]["key"]
    else:
        flag = False
        for i in season_data["data"]:
            if i["label"] == season:
                season_key = i["key"]
                flag = True
        if flag is False:
            await rank.finish(f"唔……您所提供的赛季暂时无法找到，您可以留空，这样{Config.bot_basic.bot_name}将提供最新赛季的天梯榜。")
        else:
            img = await get_school_rank(season_key)
            await rank.finish(ms.image(img))
    img = await get_school_rank(season_key)
    await rank.finish(ms.image(img))
