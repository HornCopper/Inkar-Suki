from nonebot.matcher import Matcher

from ..api import *
from .renderer import *
jx3_cmd_trade2 = on_command(
    "jx3_trade2",
    name="交易行",
    aliases={'交易'},
    priority=5,
    catalog=permission.jx3.pvg.price.trade,
    description="获取交易行物品的价格",
    example=[
        Jx3Arg(Jx3ArgsType.server),
        Jx3Arg(Jx3ArgsType.property),
        Jx3Arg(Jx3ArgsType.pageIndex, default=0)
    ],
    document='''''',
)


@jx3_cmd_trade2.handle()
async def jx3_trade2(matcher: Matcher, state: T_State, event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_server, arg_item, arg_page = template
    state["server"] = arg_server
    pageSize = 20
    data, totalCount = await search_item_info_for_price(arg_item, arg_server, pageIndex=arg_page, pageSize=pageSize)
    if not isinstance(data, List):
        return await jx3_cmd_trade2.finish(data)
    all_id = [x.id for x in data]  # 取到的是id列表
    state["id"] = all_id
    if len(all_id) == 1:  # 仅有一个物品的话，则直接显示更加详细的信息。如果没有则直接跳过
        matcher.set_arg("user_select_index", obMessage("1"))
        return
    elif len(all_id) == 0:  # 广搜没搜到，则转换为单搜
        matcher.set_arg("user_select_index", obMessage("0"))
        result = await get_jx3_trade_detail(matcher, state, event, [arg_server, arg_item])
        if isinstance(result, list):
            return await jx3_cmd_trade2.finish(result[0])
        return await jx3_cmd_trade2.send(result)

    result = await render_items(arg_server, arg_item, arg_page, pageSize, totalCount, data)
    return await jx3_cmd_trade2.send(ms.image(Path(result).as_uri()))


jx3_cmd_trade_detail = on_command(
    "jx3_cmd_trade_detail",
    name="交易行详细",
    aliases={'交易详细'},
    priority=5,
    catalog=permission.jx3.pvg.price.trade,
    description="获取交易行单个物品的价格",
    example=[
        Jx3Arg(Jx3ArgsType.server),
        Jx3Arg(Jx3ArgsType.property),
    ],
    document='''获取交易行单个物品的价格
    如果有多个候选项，则默认选取第一个''',
)


@jx3_cmd_trade_detail.handle()
async def jx3_trade_detail(matcher: Matcher, state: T_State, event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    result = await get_jx3_trade_detail(matcher, state, event, template)
    if isinstance(result, list):
        return await jx3_cmd_trade_detail.finish(result[0])
    return await jx3_cmd_trade_detail.send(result)


async def get_jx3_trade_detail(matcher: Matcher, state: T_State, event: GroupMessageEvent, template: list[Any]):
    arg_server, arg_item = template
    data = await search_item_info(arg_item, pageIndex=0, pageSize=1000)
    data = [x for x in data if x.bind_type != GoodsBindType.BindOnPick]
    if len(data) < 1:
        return ['没有找到这个物品']
    first_item = data[0]
    state['id'] = [first_item.id]
    state['server'] = arg_server

    result = await get_price_num_selected2(state, event, "1")
    return result


jx3_cmd_favouritest = on_command(
    "jx3_trade_favoritest",
    name="交易行热门",
    catalog=permission.jx3.pvg.price.trade,
    example=[
        Jx3Arg(Jx3ArgsType.server),
        Jx3Arg(Jx3ArgsType.pageIndex, default=0)
    ],
    priority=5
)


@jx3_cmd_favouritest.handle()
async def jx3_trade_favoritest(matcher: Matcher, state: T_State, event: GroupMessageEvent, template: list[Any] = Depends(Jx3Arg.arg_factory)):
    """
    获取交易行物品价格：
    交易行热门 [区服] [页码]
    Example：交易行热门 幽月轮 1
    Example：交易行热门 2
    """
    arg_server, arg_page = template
    items = get_favoritest_by_predict(lambda index, x: x.u_popularity > 100)
    pageSize = 20
    data, totalCount = await get_prices_by_items(items, arg_server, pageIndex=arg_page, pageSize=pageSize)
    if not isinstance(data, List):
        return await jx3_cmd_favouritest.finish(data)
    result = await render_items(arg_server, "热门物品", arg_page, pageSize, totalCount, data, template="goods_list_fav")
    return await jx3_cmd_favouritest.send(ms.image(Path(result).as_uri()))


@jx3_cmd_trade2.got("user_select_index")
async def price_num_selected2(state: T_State, event: GroupMessageEvent, user_select_index: Message = Arg()):
    data = await get_price_num_selected2(state, event, user_select_index.extract_plain_text())
    if data is None:
        return
    if isinstance(data, list):
        return await jx3_cmd_trade2.finish(data[0])
    return await jx3_cmd_trade2.send(data)


async def get_price_num_selected2(state: T_State, event: GroupMessageEvent, user_select_index: str):
    good_index = get_number(user_select_index)
    all_ids = state["id"]
    logger.debug(f'price_num_selected2:{good_index}@{event.group_id},all={all_ids}')
    if good_index > len(all_ids) or good_index <= 0:
        if good_index == 0:
            return  # 无视0序号
        return f"无效的序号[{good_index}]，有效范围:1-{len(all_ids)}"
    target_id = all_ids[good_index-1]
    server = server_mapping(state["server"], event.group_id)
    goods_price_log = await getItemPriceById(target_id, server)
    await update_goods_popularity(target_id, all_ids)
    if not isinstance(goods_price_log, list):
        return goods_price_log[0]
    logs, _ = goods_price_log
    good_info = await GoodsInfoFull.from_id(target_id)
    goods_price_current_detail = await get_goods_current_detail_price(target_id, server)
    result = await render_detail_item(server, good_info, goods_price_current_detail, logs)
    return ms.image(Path(result).as_uri())


jx3_cmd_trade2_refresh_job = on_command(
    "jx3_cmd_trade2_refresh_job",
    name="更新热门",
    catalog=permission.jx3.pvg.price.trade,
    example=[],
    priority=5
)


@jx3_cmd_trade2_refresh_job.handle()
async def jx3_trade2_refresh_job(event: GroupMessageEvent):
    permit = Permission(event.user_id).judge(10, '刷新交易行热门')
    if not permit.success:
        return await jx3_cmd_trade2_refresh_job.finish(permit.description)
    t = refresh_favoritest_goods_current_price()
    await jx3_cmd_trade2_refresh_job.send(f'已开始新的任务:{t.id}')
