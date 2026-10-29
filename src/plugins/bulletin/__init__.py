from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

from src.utils.command import on_command

from .app import get_bulletin_img

GladBulletinMatcher = on_command(
    "bulletin_glad",
    command_key = "喜报",
    aliases = {"喜报"},
    force_whitespace = True,
    priority = 5,
)

@GladBulletinMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    msg = args.extract_plain_text()
    if msg == "":
        await GladBulletinMatcher.finish("唔……你还没有输入喜报的内容呢！")
    elif len(msg) > 20:
        await GladBulletinMatcher.finish("字数请控制在20字以内！")
    else:
        img = await get_bulletin_img(msg, "G")
        await GladBulletinMatcher.finish(img)

SadBulletinMatcher = on_command(
    "bulletin_sad",
    command_key = "悲报",
    aliases = {"悲报"},
    force_whitespace = True,
    priority = 5,
)

@SadBulletinMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    msg = args.extract_plain_text()
    if msg == "":
        await SadBulletinMatcher.finish("唔……你还没有输入悲报的内容呢！")
    elif len(msg) > 20:
        await SadBulletinMatcher.finish("字数请控制在20字以内！")
    else:
        img = await get_bulletin_img(msg, "S")
        await SadBulletinMatcher.finish(img)
