from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

from .chutian import get_chutian_image
from .yuncong import get_yuncong_image

ChutianMatcher = on_command("jx3_chutian", aliases={"楚天社"}, force_whitespace=True, priority=5)

@ChutianMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    image = await get_chutian_image()
    await ChutianMatcher.finish(image)

YuncongMatcher = on_command("jx3_yuncong", aliases={"云从社"}, force_whitespace=True, priority=5)

@YuncongMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    image = await get_yuncong_image()
    await YuncongMatcher.finish(image)