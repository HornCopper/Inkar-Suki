from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

from .chutian import get_chutian_image
from .yuncong import get_yuncong_image

chutian_matcher = on_command("jx3_chutian", aliases={"楚天社"}, force_whitespace=True, priority=5)

@chutian_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    image = await get_chutian_image()
    await chutian_matcher.finish(image)

yuncong_matcher = on_command("jx3_yuncong", aliases={"云从社"}, force_whitespace=True, priority=5)

@yuncong_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    image = await get_yuncong_image()
    await yuncong_matcher.finish(image)