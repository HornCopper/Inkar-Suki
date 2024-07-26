from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.tools.utils.request import get_content

from .api import *

announce = on_command("jx3_announce", aliases={"维护公告", "更新公告", "公告", "更新"}, force_whitespace=True, priority=5)

@announce.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取维护公告的图片：

    Example：-维护公告
    """
    if args.extract_plain_text() != "":
        return
    url = await getAnnounce()
    url = await get_content(url)
    await announce.finish(ms.image(url))
