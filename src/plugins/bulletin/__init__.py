from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from .api import *

bulletin_glad = on_command("喜报", force_whitespace=True, priority=5)

@bulletin_glad.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    msg = args.extract_plain_text()
    if msg == "":
        await bulletin_glad.finish("唔……你还没有输入喜报的内容呢！")
    elif len(msg) > 20:
        await bulletin_glad.finish("字数请控制在20字以内！")
    else:
        img = await get_bulletinG(msg, "G")
        if not isinstance(img, str):
            return
        await bulletin_glad.finish(ms.image(img))

bulletin_sad = on_command("悲报", force_whitespace=True, priority=5)

@bulletin_sad.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    msg = args.extract_plain_text()
    if msg == "":
        await bulletin_sad.finish("唔……你还没有输入悲报的内容呢！")
    elif len(msg) > 20:
        await bulletin_sad.finish("字数请控制在20字以内！")
    else:
        img = await get_bulletinG(msg, "S")
        if not isinstance(img, str):
            return
        await bulletin_sad.finish(ms.image(img))