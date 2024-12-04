from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.network import Request

from .chutian import get_chutian_image
from .yuncong import get_yuncong_image
from .zhue import get_zhue_image

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

ZhueMatcher = on_command("jx3_zhue", aliases={"诛恶"}, force_whitespace=True, priority=5)

@ZhueMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    serverInstance = Server(args.extract_plain_text(), event.group_id)
    if serverInstance.server is None:
        await ZhueMatcher.finish(PROMPT.ServerNotExist)
    else:
        image = await get_zhue_image(serverInstance.server)
        await ZhueMatcher.finish(image)