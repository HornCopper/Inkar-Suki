from typing import Any

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment as ms

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.permission import check_permission, denied
from src.utils.analyze import check_number
from src.utils.typing import override
from src.utils.network import Request
from src.utils.database import db
from src.utils.database.classes import ItemKeywordMap
from src.utils.database.operation import get_group_settings
from src.plugins.preferences.app import Preference

from .api import get_trade_image_v2
from .item_v2 import get_single_item_price
from .shilian import get_wufeng_image
from .wanbaolou import get_wbl_role

from .trade import JX3Trade

class S(Server):
    @override
    @property
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
        

trade_v2_matcher = on_command("jx3_trade_v2", aliases={"交易行v2"}, force_whitespace=True, priority=5)

@trade_v2_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await trade_v2_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：交易行v2 <服务器> <关键词>")
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
        await trade_v2_matcher.finish(PROMPT.ServerNotExist)
    img = await get_trade_image_v2(server, name, multi_items)
    await trade_v2_matcher.finish(img)

trade_v2_sl_matcher = on_command("jx3_shilian_v2", aliases={"交易行试炼v2"}, force_whitespace=True, priority=5)

@trade_v2_sl_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await trade_v2_sl_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：交易行试炼v2 <服务器> <词条(不带空格)>")
    if len(arg) == 1:
        server = None
        msg = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        msg = arg[1]
    server = S(server, event.group_id).server
    if server is None:
        await trade_v2_sl_matcher.finish(PROMPT.ServerNotExist)
    img = await get_wufeng_image(msg, server)
    await trade_v2_sl_matcher.finish(img)

trade_matcher = on_command("jx3_trade", aliases={"交易行"}, force_whitespace=True, priority=5)

@trade_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await trade_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：交易行试炼 <服务器> <关键词>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    ver = Preference(event.user_id, "", "").setting("交易行")
    server = S(server, event.group_id).server
    if server is None:
        await trade_matcher.finish(PROMPT.ServerNotExist)
    if ver == "v2":
        multi_items = name.split(",")
        if len(multi_items) <= 1:
            multi_items = []
        if server is None:
            await trade_matcher.finish(PROMPT.ServerNotExist)
        msg = await get_trade_image_v2(server, name, multi_items)
    elif ver == "v3":
        instance = await JX3Trade.common(name, server)
        if isinstance(instance, str):
            await trade_v3_matcher.finish(instance)
        msg = await instance.generate_image()
    await trade_matcher.finish(msg)

trade_sl_matcher = on_command("jx3_shilian", aliases={"交易行试炼"}, force_whitespace=True, priority=5)

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
    elif len(arg) == 2:
        server = arg[0]
        msg = arg[1]
    server = S(server, event.group_id).server
    ver = Preference(event.user_id, "", "").setting("交易行")
    if server is None:
        await trade_sl_matcher.finish(PROMPT.ServerNotExist)
    if ver == "v2":
        image = await get_wufeng_image(msg, server)
    elif ver == "v3":
        instance = await JX3Trade.shilian(msg, server)
        if isinstance(instance, str):
            await trade_sl_matcher.finish(instance)
        image = await instance.generate_image()
    await trade_sl_matcher.finish(image)

trade_v3_matcher = on_command("jx3_trade_v3", aliases={"交易行v3"}, force_whitespace=True, priority=5)

@trade_v3_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await trade_v3_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：交易行v3 <服务器> <关键词>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = S(server, event.group_id).server
    if server is None:
        await trade_v3_matcher.finish(PROMPT.ServerNotExist)
    instance = await JX3Trade.common(name, server)
    if isinstance(instance, str):
        await trade_v3_matcher.finish(instance)
    msg = await instance.generate_image()
    await trade_v3_matcher.finish(msg)

trade_v3_sl_matcher = on_command("jx3_trade_shilian_v3", aliases={"交易行试炼v3"}, force_whitespace=True, priority=5)

@trade_v3_sl_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await trade_v3_sl_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：交易行试炼v3 <服务器> <词条(不带空格)>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = S(server, event.group_id).server
    if server is None:
        await trade_v3_sl_matcher.finish(PROMPT.ServerNotExist)
    from .trade import JX3Trade
    instance = await JX3Trade.shilian(name, server)
    if isinstance(instance, str):
        await trade_v3_sl_matcher.finish(instance)
    msg = await instance.generate_image()
    await trade_v3_sl_matcher.finish(msg)

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
    if not check_permission(event.user_id, 6):
        await item_aliases_matcher.finish(denied(6))
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