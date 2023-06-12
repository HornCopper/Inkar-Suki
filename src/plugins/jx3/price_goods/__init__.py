from src.tools.dep.bot import *
from .api import *

jx3_cmd_trade = on_command("jx3_trade", aliases={"交易行"}, priority=5)


@jx3_cmd_trade.handle()
async def jx3_trade(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取交易行物品价格：
    交易行 [区服] 名称 [页码]
    Example：-交易行 幽月轮 帝骖龙翔 1
    Example：-交易行 帝骖龙翔 2
    '''
    arg = args.extract_plain_text().split(" ")
    arg = extensions.list2dict(arg)
    arg_len = len(arg)
    if arg_len == 0:
        return await jx3_cmd_trade.finish(f"{PROMPT_ArgumentInvalid}如 交易行 帝骖龙翔 1")

    arg_server = server_mapping(arg.get(0))
    if not arg_server: # 重置参数
        arg = extensions.list2dict([None, arg.get(0), arg.get(1)])
    arg_item, arg_page = arg.get(1), get_number(arg.get(2))

    arg_page = 0 if arg_page <= 1 else arg_page - 1  # 从第0页起算
    server = server_mapping(arg_server, group_id=str(event.group_id))
    if not server:
        return await jx3_cmd_trade.finish(PROMPT_ServerNotExist)
    state["server"] = server
    data = await search_item_info(arg_item, pageIndex=arg_page)
    if type(data) != type([]):
        return jx3_cmd_trade.finish(data)
    id = data[0]  # 取到的是id列表
    state["id"] = id
    return await jx3_cmd_trade.send(ms.image(Path(data[1]).as_uri()))


@jx3_cmd_trade.got("num", prompt="输入序号以搜索，其他内容则无视。")
async def price_num_selected(state: T_State, event: GroupMessageEvent, num: Message = Arg()):
    num = num.extract_plain_text()
    if not checknumber(num):
        return
    all_ids = state["id"]
    id = all_ids[int(num)]
    server = state["server"]
    data = await getItemPriceById(id, server, all_ids, group_id=event.group_id)
    if type(data) != type([]):
        return await jx3_cmd_trade.finish(data)
    else:
        img = data[0]
        return await jx3_cmd_trade.send(ms.image(Path(img).as_uri()))

jx3_cmd_item = on_command("jx3_item", aliases={"物品"}, priority=5)


@jx3_cmd_item.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    id = args.extract_plain_text()
    info = await getItem(id)
    if type(info) == type([]):
        return await jx3_cmd_item.finish(info[0])
    else:
        return await jx3_cmd_item.finish(ms.image(Path(info).as_uri()))
