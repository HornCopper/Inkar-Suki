from .trend import *

trade = on_command("jx3_trade", aliases={"交易行"}, priority=5)


@trade.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
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

trade_wf = on_command("jx3_wufeng", aliases={"交易行无封"}, priority=5)


@trade_wf.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
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

# 施工中
# trade_trend = on_command("jx3_trend", aliases={"交易行走势"}, priority=5)

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