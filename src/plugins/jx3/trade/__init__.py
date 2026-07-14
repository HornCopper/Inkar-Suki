from typing import Any

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment as ms

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.config import Config
from src.utils.permission import check_permission, denied
from src.utils.analyze import check_number
from src.utils.typing import override
from src.utils.network import Request
from src.utils.database import db
from src.utils.database.classes import ItemKeywordMap
from src.utils.database.operation import get_group_settings

from .price import get_single_item_price
from .wanbaolou import get_wbl_role
from .auction import get_auction_image

from .market import JX3Trade

class TradeServer(Server):
    @property
    @override
    def server(self) -> str | None:
        if self._server == "全服":
            return "全服"
        if self._server is None and self.group_id is not None:
            final_server = get_group_settings(self.group_id, "server") or None
        elif self._server is not None:
            final_server = self.server_raw
            if final_server is None and self.group_id:
                final_server = get_group_settings(self.group_id, "server") or None
        else:
            final_server = None
        return final_server


auction_matcher = on_command(
    "jx3_auction",
    aliases={"阵营拍卖", "拍卖"},
    force_whitespace=True,
    priority=5,
)


@auction_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if not Config.jx3.api.enable:
        return

    argument = args.extract_plain_text().strip()
    parts = argument.split(maxsplit=1) if argument else []
    bound_server = TradeServer(None, event.group_id).server
    server: str | None = None
    name = ""

    if not parts:
        server = bound_server
    elif len(parts) == 1:
        explicit_server = Server(parts[0]).server
        if explicit_server:
            server = explicit_server
        elif bound_server:
            server = bound_server
            name = parts[0]
    else:
        server = Server(parts[0]).server
        name = parts[1].strip()

    if server is None:
        await auction_matcher.finish(
            PROMPT.ServerNotExist
            + "\n参考格式：阵营拍卖 <服务器> [物品名]"
            + "\n群聊已绑定服务器时，可以省略服务器。"
        )

    image = await get_auction_image(server, name)
    await auction_matcher.finish(image)
        

trade_matcher = on_command(
    "jx3_trade_v3",
    aliases={"jx3_trade", "交易行", "交易行v2", "交易行v3"},
    force_whitespace=True,
    priority=5,
)

@trade_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await trade_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：交易行 <服务器> <关键词>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    else:
        server = arg[0]
        name = arg[1]
    server = TradeServer(server, event.group_id).server
    if server is None:
        await trade_matcher.finish(PROMPT.ServerNotExist)
    instance = await JX3Trade.common(name, server)
    if isinstance(instance, str):
        await trade_matcher.finish(instance)
    msg = await instance.generate_image()
    await trade_matcher.finish(msg)

trade_sl_matcher = on_command(
    "jx3_trade_shilian_v3",
    aliases={"jx3_shilian", "交易行试炼", "交易行试炼v2", "交易行试炼v3"},
    force_whitespace=True,
    priority=5,
)

@trade_sl_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await trade_sl_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：交易行试炼 <服务器> <词条(不带空格)>")
    if len(arg) == 1:
        server = None
        msg = arg[0]
    else:
        server = arg[0]
        msg = arg[1]
    server = TradeServer(server, event.group_id).server
    if server is None:
        await trade_sl_matcher.finish(PROMPT.ServerNotExist)
    instance = await JX3Trade.shilian(msg, server)
    if isinstance(instance, str):
        await trade_sl_matcher.finish(instance)
    image = await instance.generate_image()
    await trade_sl_matcher.finish(image)

item_price_v2_matcher = on_command("jx3_item_v2", aliases={"物价v2", "物价"}, force_whitespace=True, priority=5)

@item_price_v2_matcher.handle()
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
        await item_price_v2_matcher.finish(data[0])
    elif isinstance(data, dict):
        aliases = list(set(data["v"]))
        if len(aliases) > 20:
            aliases = aliases[:20]
        if len(aliases) == 0:
            await item_price_v2_matcher.finish("唔……未找到该物品！\n请确认是否应该使用“交易行”命令？")
        if len(aliases) == 1:
            img = await get_single_item_price(aliases[0], True)
            if not isinstance(img, str):
                return
            img_content = Request(img).local_content
            await item_price_v2_matcher.finish(ms.image(img_content))
        state["v"] = aliases
        msg = "音卡找到下面的相关物品，请回复前方序号来搜索！"
        for num, name in enumerate(aliases, start=1):
            msg += f"\n[{num}] {name}"
        await item_price_v2_matcher.send(msg)
        return
    elif isinstance(data, str):
        img = Request(data).local_content
        await item_price_v2_matcher.finish(ms.image(img))

@item_price_v2_matcher.got("num")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num_ = num.extract_plain_text()
    data = state["v"]
    if not check_number(num_):
        await item_price_v2_matcher.finish("唔……输入的不是数字，取消搜索。")
    if int(num_) > len(data):
        await item_price_v2_matcher.finish("唔……不存在该数字对应的搜索结果，请重新搜索！")
    name = data[int(num_)-1]
    img = await get_single_item_price(name, True)
    if not isinstance(img, str):
        return
    img_content = Request(img).local_content
    await item_price_v2_matcher.finish(ms.image(img_content))

wanbaolou_role_matcher = on_command("jx3_wbl", aliases={"万宝楼"}, priority=5, force_whitespace=True)

@wanbaolou_role_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    num = args.extract_plain_text()
    if num == "":
        return
    if not check_number(num):
        return
    msg = await get_wbl_role(int(num))
    await wanbaolou_role_matcher.finish(msg)

item_aliases_matcher = on_command("jx3_itemaliases", aliases={"物品别名", "物品别称"}, priority=5, force_whitespace=True)

@item_aliases_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    if not check_permission(event.user_id, "jx3.trade.item_alias.manage"):
        await item_aliases_matcher.finish(denied("jx3.trade.item_alias.manage"))
    args = argument.extract_plain_text().split(" ")
    if len(args) != 2:
        await item_aliases_matcher.finish("唔……参数数量不正确，请参考命令格式：\n物品别名 别名 实际名")
    map_name = args[0]
    raw_name = args[1]
    local_data: ItemKeywordMap | None | Any = db.where_one(ItemKeywordMap(), "raw_name = ?", map_name, default=None)
    if local_data is not None:
        await item_aliases_matcher.finish("无法继续添加别名映射：检测到重复别名！")
    db.save(
        ItemKeywordMap(
            map_name=map_name,
            raw_name=raw_name
        )
    )
    await item_aliases_matcher.finish(f"已添加物品别名映射：{map_name} -> {raw_name}！")
