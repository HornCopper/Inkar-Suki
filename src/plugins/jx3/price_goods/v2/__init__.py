from nonebot.matcher import Matcher

from ..api import *
from .renderer import *
jx3_cmd_trade2 = on_command("jx3_trade2", aliases={"交易行"}, priority=5)


@jx3_cmd_trade2.handle()
async def jx3_trade2(matcher: Matcher, state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取交易行物品价格：
    交易行 [区服] 名称 [页码]
    Example：交易行 幽月轮 帝骖龙翔 1
    Example：交易行 帝骖龙翔 2
    """
    arg = get_trade2_args(event, args)
    if not isinstance(arg, List):
        return await jx3_cmd_trade2.finish(arg)
    arg_server, arg_item, arg_page = arg
    return await handle_trade2(matcher, state, arg_server, arg_item, arg_page)


def get_trade2_args(event: GroupMessageEvent, args: Message = CommandArg()):
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(
        Jx3ArgsType.default), Jx3Arg(Jx3ArgsType.pageIndex)]
    arg = get_args(args, template)
    logger.debug(f"user trade-input :{arg}")
    if isinstance(arg, InvalidArgumentException):
        return f"{PROMPT_ArgumentInvalid}如 价格 帝骖龙翔 1"
    arg_server, arg_item, arg_page = arg
    arg_server = server_mapping(arg_server, group_id=str(event.group_id))
    arg_page = 0 if arg_page is None or arg_page <= 1 else arg_page - 1  # 从第0页起算
    if not arg_server:
        return PROMPT_ServerNotExist
    return [arg_server, arg_item, arg_page]


async def handle_trade2(matcher: Matcher, state: T_State, arg_server: str, arg_item: str, arg_page: int):
    state["server"] = arg_server
    pageSize = 20
    data, totalCount = await search_item_info_for_price(arg_item, arg_server, pageIndex=arg_page, pageSize=pageSize)
    if not isinstance(data, List):
        return await jx3_cmd_trade2.finish(data)
    all_id = [x.id for x in data]  # 取到的是id列表
    state["id"] = all_id
    if len(all_id) <= 1:  # 仅有一个物品的话，则直接显示更加详细的信息。如果没有则直接跳过
        matcher.set_arg("user_select_index", obMessage("1"))
        return
    result = await render_items(arg_server, arg_item, arg_page, pageSize, totalCount, data)
    return await jx3_cmd_trade2.send(ms.image(Path(result).as_uri()))

jx3_cmd_favouritest = on_command("jx3_trade_favoritest", aliases={"交易行热门"}, priority=5)


@jx3_cmd_favouritest.handle()
async def jx3_trade_favoritest(matcher: Matcher, state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取交易行物品价格：
    交易行热门 [区服] [页码]
    Example：交易行热门 幽月轮 1
    Example：交易行热门 2
    """
    arg = get_trade2_args(event, args)
    if not isinstance(arg, List):
        return await jx3_cmd_favouritest.finish(arg)
    arg_server, _, arg_page = arg
    items = get_favoritest_by_predict(lambda index, x: x.u_popularity > 100)
    pageSize = 20
    data, totalCount = await get_prices_by_items(items, arg_server, pageIndex=arg_page, pageSize=pageSize)
    if not isinstance(data, List):
        return await jx3_cmd_favouritest.finish(data)
    result = await render_items(arg_server, "热门物品", arg_page, pageSize, totalCount, data, template="goods_list_fav")
    return await jx3_cmd_favouritest.send(ms.image(Path(result).as_uri()))


@jx3_cmd_trade2.got("user_select_index")
async def price_num_selected2(state: T_State, event: GroupMessageEvent, user_select_index: Message = Arg()):
    good_index = get_number(user_select_index.extract_plain_text())
    all_ids = state["id"]
    if len(all_ids) == 0:
        return # 没有项可以选择
    if good_index > len(all_ids) or good_index <= 0:
        return await jx3_cmd_trade2.finish(f"无效的序号[{good_index}]，有效范围:1-{len(all_ids)}")
    target_id = all_ids[good_index-1]
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


jx3_cmd_trade2_refresh_job = on_command("jx3_cmd_trade2_refresh_job", aliases={"更新热门"}, priority=5)


@jx3_cmd_trade2_refresh_job.handle()
async def jx3_trade2_refresh_job(event: GroupMessageEvent):
    permit = Permission(event.user_id).judge(10, '刷新交易行热门')
    if not permit.success:
        return await jx3_cmd_trade2_refresh_job.finish(permit.description)
    t = refresh_favoritest_goods_current_price()
    await jx3_cmd_trade2_refresh_job.send(f'已开始新的任务:{t.id}')
