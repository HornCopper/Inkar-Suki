from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.tools.utils.file import get_content_local

from .api import getCalendar

calendar = on_command("jx3_calendar", aliases={"活动日历", "剑三日历"}, force_whitespace=True, priority=5)

@calendar.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    image = await getCalendar()
    if not isinstance(image, str):
        return
    image = get_content_local(image)
    await calendar.finish(ms.image(image))