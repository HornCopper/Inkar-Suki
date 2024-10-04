from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.analyze import check_number
from src.utils.typing import override
from src.utils.network import Request
from src.utils.database.operation import get_group_settings

from .api import get_trade_image
from .item_v2 import get_single_item_price
from .wufeng import get_wufeng_image

class S(Server):
    @override
    @property
    def server(self) -> str | None:
        if self._server == "全服":
            return "全服"
        if self._server is None and self.group_id is not None:
            final_server = get_group_settings(self.group_id)
        elif self._server is not None:
            final_server = self.server_raw
            if final_server is None and self.group_id:
                final_server = get_group_settings(self.group_id)
        else:
            final_server = None
        return final_server
        

TradeMatcher = on_command("jx3_trade", aliases={"交易行"}, force_whitespace=True, priority=5)

@TradeMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await TradeMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    multi_items = name.split(",")
    if len(multi_items) <= 1:
        multi_items = []
    server = S(server, event.group_id).server
    if server is None:
        await TradeMatcher.finish(PROMPT.ServerNotExist)
    img = await get_trade_image(server, name, multi_items)
    if isinstance(img, list):
        await TradeMatcher.finish(img[0])
    elif isinstance(img, str):
        await TradeMatcher.finish(ms.image(img))


WFTradeMatcher = on_command("jx3_wufeng", aliases={"交易行无封"}, force_whitespace=True, priority=5)

@WFTradeMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await WFTradeMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        msg = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        msg = arg[1]
    server = S(server, event.group_id).server
    if server is None:
        await TradeMatcher.finish(PROMPT.ServerNotExist)
    img = await get_wufeng_image(msg, server)
    if isinstance(img, list):
        await WFTradeMatcher.finish(img[0])
    elif isinstance(img, str):
        await WFTradeMatcher.finish(ms.image(img))

V2ItemPriceMatcher = on_command("jx3_item_v2", aliases={"物价v2", "物价"}, force_whitespace=True, priority=5)

@V2ItemPriceMatcher.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    """
    获取外观物价：
    Example：-物价v2 山神盒子
    Example：-物价v2 大橙武券
    """
    if args.extract_plain_text() == "":
        return
    data = await get_single_item_price(args.extract_plain_text())
    if isinstance(data, list):
        await V2ItemPriceMatcher.finish(data[0])
    elif isinstance(data, dict):
        aliases = data["v"]
        if len(aliases) > 20:
            aliases = aliases[:20]
        if len(aliases) == 0:
            await V2ItemPriceMatcher.finish("唔……未找到该物品！")
        if len(aliases) == 1:
            img = await get_single_item_price(aliases[0], True)
            if not isinstance(img, str):
                return
            img_content = Request(img).local_content
            await V2ItemPriceMatcher.finish(ms.image(img_content))
        state["v"] = aliases
        msg = "音卡找到下面的相关物品，请回复前方序号来搜索！"
        for num, name in enumerate(aliases, start=1):
            msg += f"\n[{num}] {name}"
        await V2ItemPriceMatcher.send(msg)
        return
    elif isinstance(data, str):
        img = Request(data).local_content
        await V2ItemPriceMatcher.finish(ms.image(img))

@V2ItemPriceMatcher.got("num")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num_ = num.extract_plain_text()
    data = state["v"]
    if not check_number(num_):
        await V2ItemPriceMatcher.finish("唔……输入的不是数字，取消搜索。")
    if int(num_) > len(data):
        await V2ItemPriceMatcher.finish("唔……不存在该数字对应的搜索结果，请重新搜索！")
    name = data[int(num_)-1]
    img = await get_single_item_price(name, True)
    if not isinstance(img, str):
        return
    img_content = Request(img).local_content
    await V2ItemPriceMatcher.finish(ms.image(img_content))