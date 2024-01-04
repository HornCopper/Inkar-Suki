from nonebot.matcher import Matcher

from ..api import *
from .renderer import *
jx3_cmd_trade2 = on_command(
    "jx3_trade2",
    aliases={"交易行"},
    priority=5,
    catalog='jx3.pvg.price.trade@v2',
    description="获取交易行物品的价格",
    example=[
        Jx3Arg(Jx3ArgsType.server),
        Jx3Arg(Jx3ArgsType.default),
        Jx3Arg(Jx3ArgsType.pageIndex, default=0)
    ],
    document='''''',
)


@jx3_cmd_trade2.handle()
async def jx3_trade2(matcher: Matcher, state: T_State, event: GroupMessageEvent, template: list[Jx3Arg] = None):
    """
    获取交易行物品价格：
    交易行 [区服] 名称 [页码]
    Example：交易行 幽月轮 帝骖龙翔 1
    Example：交易行 帝骖龙翔 2
    """
    arg_server, arg_item, arg_page = template
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

jx3_cmd_favouritest = on_command(
    "jx3_trade_favoritest",
    aliases={"交易行热门"},
    catalog='jx3.pvg.price.trade-hot',
    example=[
        Jx3Arg(Jx3ArgsType.server),
        Jx3Arg(Jx3ArgsType.pageIndex, default=0)
    ],
    priority=5
)


@jx3_cmd_favouritest.handle()
async def jx3_trade_favoritest(matcher: Matcher, state: T_State, event: GroupMessageEvent, template: list[Jx3Arg] = None):
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
    good_index = get_number(user_select_index.extract_plain_text())
    all_ids = state["id"]
    if len(all_ids) == 0:
        return  # 没有项可以选择
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


jx3_cmd_trade2_refresh_job = on_command(
    "jx3_cmd_trade2_refresh_job",
    aliases={"更新热门"},
    catalog='jx3.pvg.price.trade-update',
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
