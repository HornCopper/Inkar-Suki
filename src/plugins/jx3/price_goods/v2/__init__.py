from src.tools.dep.bot import *
from ..api import *
from .renderer import *
jx3_cmd_trade2 = on_command("jx3_trade2", aliases={"价格"}, priority=5)


@jx3_cmd_trade2.handle()
async def jx3_trade2(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取交易行物品价格：
    交易行 [区服] 名称 [页码]
    Example：-交易行 幽月轮 帝骖龙翔 1
    Example：-交易行 帝骖龙翔 2
    '''
    template = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(
        Jx3ArgsType.default), Jx3Arg(Jx3ArgsType.pageIndex)]
    arg = get_args(args, template)
    if isinstance(arg, InvalidArgumentException):
        return await jx3_cmd_trade2.finish(f"{PROMPT_ArgumentInvalid}如 交易行 帝骖龙翔 1")
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

    id = [x.id for x in data]  # 取到的是id列表
    result = await render_items(arg_server, arg_item, arg_page, pageSize, totalCount, data)
    state["id"] = id
    return await jx3_cmd_trade2.send(ms.image(Path(result).as_uri()))


# @jx3_cmd_trade2.got("num2")
# async def price_num_selected2(state: T_State, event: GroupMessageEvent, num: Message = Arg()):
#     num = num.extract_plain_text()
#     num = get_number(num)
#     all_ids = state["id"]
#     if num >= len(all_ids):
#         return await jx3_cmd_trade2.finish(f'无效的序号，有效范围:0-{len(all_ids)}')

#     id = all_ids[num]
#     server = state["server"]
#     data = await getItemPriceById(id, server, all_ids, group_id=event.group_id)
#     if type(data) != type([]):
#         return await jx3_cmd_trade2.finish(data)
#     else:
#         img = data[0]
#         return await jx3_cmd_trade2.send(ms.image(Path(img).as_uri()))
