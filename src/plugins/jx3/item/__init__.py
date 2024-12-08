from nonebot import on_command
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment as ms

from src.utils.analyze import check_number

from .item import get_item_info, get_item_image

ItemSearcherMatcher = on_command("jx3_item", aliases={"物品"}, priority=5, force_whitespace=True)

@ItemSearcherMatcher.handle()
async def _(event: GroupMessageEvent, state: T_State, argument: Message = CommandArg()):
    item_name = argument.extract_plain_text().strip()
    msg = await get_item_info(item_name)
    if isinstance(msg, ms):
        await ItemSearcherMatcher.finish(msg)
    elif isinstance(msg, tuple):
        reply, data = msg
        state["d"] = data
        await ItemSearcherMatcher.send(reply)
        return
    else:
        await ItemSearcherMatcher.finish(msg)
    await ItemSearcherMatcher.finish(msg)

@ItemSearcherMatcher.got("num")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    data: list[str] = state["d"]
    if not check_number(num.extract_plain_text().strip()) or int(num.extract_plain_text().strip()) not in list(range(len(data) + 1)):
        await ItemSearcherMatcher.finish("无法识别该序号，请重新发起命令！")
    else:
        item_id = data[int(num.extract_plain_text().strip()) - 1]
        image = await get_item_image(item_id)
        await ItemSearcherMatcher.finish(image)