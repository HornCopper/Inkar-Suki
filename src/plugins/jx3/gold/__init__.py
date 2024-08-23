from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.tools.file import get_content_local

from .api import *

demon = on_command("jx3_demon", aliases={"金价"}, force_whitespace=True, priority=5)


@demon.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取各服金价：

    Example：-金价 幽月轮
    """
    server = args.extract_plain_text()
    data = await demon_(server, group_id=str(event.group_id))
    if isinstance(data, list):
        await demon.finish(data[0])
    if isinstance(data, str):
        data = get_content_local(data)
        await demon.finish(ms.image(data))
