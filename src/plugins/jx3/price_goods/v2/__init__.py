from nonebot.matcher import Matcher
from src.tools.dep.bot import *
from ..api import *
from .renderer import *
jx3_cmd_trade2 = on_command("jx3_trade2", aliases={"交易行"}, priority=5)


@jx3_cmd_trade2.handle()
async def jx3_trade2(matcher: Matcher, state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取交易行物品价格：
    交易行 [区服] 名称 [页码]
    Example：价格 幽月轮 帝骖龙翔 1
    Example：价格 帝骖龙翔 2
    '''
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(
        Jx3ArgsType.default), Jx3Arg(Jx3ArgsType.pageIndex)]
    arg = get_args(args, template)
    if isinstance(arg, InvalidArgumentException):
        return await jx3_cmd_trade2.finish(f"{PROMPT_ArgumentInvalid}如 价格 帝骖龙翔 1")
    arg_server, arg_item, arg_page = arg
    arg_server = server_mapping(arg_server, group_id=str(event.group_id))
    arg_page = 0 if arg_page is None or arg_page <= 1 else arg_page - 1  # 从第0页起算
    if not arg_server:
        return await jx3_cmd_trade2.finish(PROMPT_ServerNotExist)
    state["server"] = arg_server
    pageSize = 20
    data, totalCount = await search_item_info_for_price(arg_item, arg_server, pageIndex=arg_page, pageSize=pageSize)
    if not isinstance(data, List):
        return await jx3_cmd_trade2.finish(data)

    all_id = [x.id for x in data]  # 取到的是id列表
    state["id"] = all_id
    if len(all_id) == 1:  # 仅有一个物品的话，则直接显示更加详细的信息
        matcher.set_arg('user_select_index', obMessage('0'))
        return
    result = await render_items(arg_server, arg_item, arg_page, pageSize, totalCount, data)

    return await jx3_cmd_trade2.send(ms.image(Path(result).as_uri()))


@jx3_cmd_trade2.got("user_select_index")
async def price_num_selected2(state: T_State, event: GroupMessageEvent, user_select_index: Message = Arg()):
    num = get_number(user_select_index.extract_plain_text())
    all_ids = state["id"]
    if num >= len(all_ids):
        return await jx3_cmd_trade2.finish(f'无效的序号，有效范围:0-{len(all_ids)}')
    target_id = all_ids[num]
    server = server_mapping(state["server"], event.group_id)

    goods_price_log = await getItemPriceById(target_id, server)
    await update_goods_popularity(target_id, all_ids)
    if type(goods_price_log) != type([]):
        return await jx3_cmd_trade2.finish(goods_price_log)

    logs, _ = goods_price_log
    good_info = await GoodsInfoFull.from_id(target_id)
    goods_price_current_detail = await get_goods_current_detail_price(target_id, server)
    result = await render_detail_item(server, good_info, goods_price_current_detail, logs)
    return await jx3_cmd_trade2.send(ms.image(Path(result).as_uri()))
