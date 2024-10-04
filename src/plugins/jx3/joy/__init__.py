from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.rule import to_me

from src.config import Config
from src.utils.network import Request

SaohuaMatcher = on_command("jx3_random", aliases={"骚话", "烧话"}, force_whitespace=True, priority=5)


@SaohuaMatcher.handle()
async def jx3_saohua_random(args: Message = CommandArg()):
    """
    召唤一条骚话：

    Example：-骚话
    """
    if args.extract_plain_text() != "":
        return
    full_link = f"{Config.jx3.api.url}/data/saohua/random"
    info = (await Request(full_link).get()).json()
    msg = info["data"]["text"]
    await SaohuaMatcher.finish(msg)

TiangouMatcher = on_command("jx3_tiangou", aliases={"舔狗", "舔狗日记"}, force_whitespace=True, priority=5)


@TiangouMatcher.handle()
async def jx3_saohua_tiangou(args: Message = CommandArg()):
    """
    获取一条舔狗日志：

    Example：-舔狗
    """
    if args.extract_plain_text() != "":
        return
    full_link = f"{Config.jx3.api.url}/data/saohua/content"
    info = (await Request(full_link).get()).json()
    msg = info["data"]["text"]
    await TiangouMatcher.finish(msg)