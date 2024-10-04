from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from .api import get_bulletin_img

GladBulletinMatcher = on_command(
    "bulletin_glad", 
    aliases={"喜报"}, 
    force_whitespace=True, 
    priority=5
)

@GladBulletinMatcher.handle()
async def _(
    event: GroupMessageEvent, 
    args: Message = CommandArg()
):
    if args.extract_plain_text() == "":
        return
    msg = args.extract_plain_text()
    if msg == "":
        await GladBulletinMatcher.finish("唔……你还没有输入喜报的内容呢！")
    elif len(msg) > 20:
        await GladBulletinMatcher.finish("字数请控制在20字以内！")
    else:
        img = await get_bulletin_img(msg, "G")
        if not isinstance(img, str):
            return
        await GladBulletinMatcher.finish(ms.image(img))

SadBulletinMatcher = on_command(
    "bulletin_sad", 
    aliases={"悲报"}, 
    force_whitespace=True, 
    priority=5
)

@SadBulletinMatcher.handle()
async def _(
    event: GroupMessageEvent, 
    args: Message = CommandArg()
):
    if args.extract_plain_text() == "":
        return
    msg = args.extract_plain_text()
    if msg == "":
        await SadBulletinMatcher.finish("唔……你还没有输入悲报的内容呢！")
    elif len(msg) > 20:
        await SadBulletinMatcher.finish("字数请控制在20字以内！")
    else:
        img = await get_bulletin_img(msg, "S")
        if not isinstance(img, str):
            return
        await SadBulletinMatcher.finish(ms.image(img))