from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.tools.file import get_content_local
from src.tools.utils.request import get_content
from src.tools.permission import checker, error

from .api import *
from .item import *
from .item_v2 import *
from .sl import *
from .wufeng import *

trade = on_command("jx3_trade", aliases={"交易行"}, force_whitespace=True, priority=5)

@trade.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await trade.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    id_cut = id.split(",")
    if len(id_cut) <= 1:
        id_cut = []
    img = await getImg(server, id, str(event.group_id), id_cut)
    if type(img) == type([]):
        await trade.finish(img[0])
    else:
        await trade.finish(ms.image(img))


trade_wf = on_command("jx3_wufeng", aliases={"交易行无封"}, force_whitespace=True, priority=5)

@trade_wf.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await trade_wf.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        msg = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        msg = arg[1]
    img = await getWufengImg(msg, server, str(event.group_id))
    if type(img) == type([]):
        await trade.finish(img[0])
    else:
        await trade.finish(ms.image(img))


item_price = on_command("jx3_price", aliases={"物价v1", "价格v1"}, force_whitespace=True, priority=5)

@item_price.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取外观物价：
    Example：-物价 山神盒子
    Example：-物价 大橙武券
    """
    if args.extract_plain_text() == "":
        return
    # arg = args.extract_plain_text()
    # if arg == "":
    #     await item_price.finish("缺少物品名称，没办法找哦~")
    # data = await item_(arg)
    # if isinstance(data, str):
    #     final_image = await get_content(data)
    #     await item_price.finish(ms.image(final_image))
    # await item_price.finish(data[0])

item_v2_ = on_command("jx3_item_v2", aliases={"物价v2", "物价"}, force_whitespace=True, priority=5)

@item_v2_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取外观物价：
    Example：-物价v2 山神盒子
    Example：-物价v2 大橙武券
    """
    if args.extract_plain_text() == "":
        return
    image = await getSingleItemPrice(args.extract_plain_text())
    if type(image) == type([]):
        await item_v2_.finish(image[0])
    else:
        img = get_content_local(image)
        await item_v2_.finish(ms.image(img))    

sl_ = on_command("jx3_sl", aliases={"无封"}, priority=5, force_whitespace=True)

@sl_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    image = await getSingleEquipment(args.extract_plain_text())
    if type(image) == type([]):
        await sl_.finish(image[0])
    else:
        image = get_content_local(image)
        await sl_.finish(ms.image(image))

item_aliases = on_command("jx3_aliases_item", aliases={"物品别名"}, force_whitespace=True, priority=5)

@item_aliases.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    if not checker(str(event.user_id), 8):
        await item_aliases.finish(error(8))
    arg = args.extract_plain_text().split(" ")
    if len(arg) != 2:
        await item_aliases.finish(PROMPT.ArgumentCountInvalid)
    raw_name = arg[0]
    formal_name = arg[1]
    current_data = json.loads(read(TOOLS + "/item_aliases.json", "{}"))
    if raw_name in current_data:
        await item_aliases.finish("唔……该物品已经存在别称了，请联系机器人Owner进行后台删除后重新操作！")
    else:
        current_data[raw_name] = formal_name
        write(TOOLS + "/item_aliases.json", json.dumps(current_data, ensure_ascii=False))
        await item_aliases.finish("添加成功！")


# 施工中
# trade_trend = on_command("jx3_trend", aliases={"交易行走势"}, force_whitespace=True, priority=5)

# @trade_trend.handle()
# async def _(event: GroupMessageEvent, args: Message = CommandArg()):
#     arg = args.extract_plain_text().split(" ")
#     if len(arg) not in [1, 2]:
#         await trade_trend.finish("唔……参数不正确哦，请检查后重试~")
#     if len(arg) == 1:
#         server = None
#         msg = arg[0]
#     elif len(arg) == 2:
#         server = arg[0]
#         msg = arg[1]
#     img = await getTrend(msg, server, str(event.group_id))
#     if type(img) == type([]):
#         await trade.finish(img[0])
#     else:
#         await trade.finish(ms.image(img))