from nonebot import on_command
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment as ms

from src.utils.analyze import check_number

from .item import get_item_info, get_item_image

item_detail_matcher = on_command("jx3_item", aliases={"物品"}, priority=5, force_whitespace=True)

@item_detail_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, argument: Message = CommandArg()):
    item_name = argument.extract_plain_text().strip()
    msg = await get_item_info(item_name)
    if isinstance(msg, ms):
        await item_detail_matcher.finish(msg)
    elif isinstance(msg, tuple):
        reply, data = msg
        state["d"] = data
        await item_detail_matcher.send(reply)
        return
    else:
        await item_detail_matcher.finish(msg)
    await item_detail_matcher.finish(msg)

@item_detail_matcher.got("num")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    data: list[str] = state["d"]
    if not check_number(num.extract_plain_text().strip()) or int(num.extract_plain_text().strip()) not in list(range(len(data) + 1)):
        await item_detail_matcher.finish("无法识别该序号，请重新发起命令！")
    else:
        item_id = data[int(num.extract_plain_text().strip()) - 1]
        image = await get_item_image(item_id)
        await item_detail_matcher.finish(image)