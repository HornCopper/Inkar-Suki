from src.tools.dep.bot import *
from ..api import *
from .renderer import *
jx3_cmd_trade = on_command("jx3_trade", aliases={"交易行v1"}, priority=5)


@jx3_cmd_trade.handle()
async def jx3_trade(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取交易行物品价格：
    交易行v1 [区服] 名称 [页码]
    Example：交易行v1 幽月轮 帝骖龙翔 1
    Example：交易行v1 帝骖龙翔 2
    '''
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(
        Jx3ArgsType.default), Jx3Arg(Jx3ArgsType.pageIndex)]
    arg = get_args(args, template)
    if isinstance(arg, InvalidArgumentException):
        return await jx3_cmd_trade.finish(f"{PROMPT_ArgumentInvalid}如 交易行 帝骖龙翔 1")
    arg_server, arg_item, arg_page = arg
    arg_server = server_mapping(arg_server, group_id=str(event.group_id))
    arg_page = 0 if arg_page is None or arg_page <= 1 else arg_page - 1  # 从第0页起算
    if not arg_server:
        return await jx3_cmd_trade.finish(PROMPT_ServerNotExist)
    state["server"] = arg_server
    data = await search_item_info(arg_item, pageIndex=arg_page)
    if type(data) != type([]):
        return await jx3_cmd_trade.finish(data)
    id = [x.id for x in data]  # 取到的是id列表
    data = await render_items(data)
    state["id"] = id
    return await jx3_cmd_trade.send(ms.image(Path(data[1]).as_uri()))


@jx3_cmd_trade.got("num", prompt="输入序号以搜索，其他内容则无视。")
async def price_num_selected(state: T_State, event: GroupMessageEvent, num: Message = Arg()):
    num = get_args(num, [Jx3Arg(Jx3ArgsType.number)])
    all_ids = state["id"]
    if num[0] >= len(all_ids):
        return await jx3_cmd_trade.finish(f'无效的序号，有效范围:0-{len(all_ids) - 1}')

    target_id = all_ids[num[0]]
    server = server_mapping(state["server"], group_id=event.group_id)
    data, goods_info = await getItemPriceById(target_id, server)
    await update_goods_popularity(target_id, all_ids)

    if goods_info is None:
        return await jx3_cmd_trade.finish(data)
    else:
        img = await render_price(data, server, goods_info)
        return await jx3_cmd_trade.send(ms.image(Path(img).as_uri()))

jx3_cmd_item = on_command("jx3_item", aliases={"物品"}, priority=5)


@jx3_cmd_item.handle()
async def jx3_item(event: GroupMessageEvent, args: Message = CommandArg()):
    id = args.extract_plain_text()
    info = await getItem(id)
    if type(info) == type([]):
        return await jx3_cmd_item.finish(info[0])
    else:
        info = await render_item_img(info)
        return await jx3_cmd_item.finish(ms.image(Path(info).as_uri()))
