from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from .item import get_item_info

ItemSearcherMatcher = on_command("jx3_item", aliases={"物品"}, priority=5, force_whitespace=True)

@ItemSearcherMatcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    item_name = argument.extract_plain_text().strip()
    msg = await get_item_info(item_name)
    await ItemSearcherMatcher.finish(msg)