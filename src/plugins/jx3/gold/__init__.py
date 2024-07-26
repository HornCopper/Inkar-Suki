from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.tools.utils.request import get_content

from .api import *

demon = on_command("jx3_demon", aliases={"金价"}, force_whitespace=True, priority=5)


@demon.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取各服金价：

    Example：-金价 幽月轮
    """
    server = args.extract_plain_text()
    data = await demon_(server, group_id=event.group_id)
    if isinstance(data, list):
        await demon.finish(data[0])
    data = await get_content(data)
    await demon.finish(ms.image(data))
