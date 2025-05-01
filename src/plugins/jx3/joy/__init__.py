from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment as ms

from src.config import Config
from src.const.prompts import PROMPT
from src.utils.network import Request

from .random_loot import RandomLoot

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

RandomLootMatcher = on_command("jx3_rdloot", aliases={"黑本", "模拟掉落"}, force_whitespace=True, priority=5)

@RandomLootMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg == "":
        return
    msg = msg.split(" ")
    if len(msg) != 2:
        return PROMPT.ArgumentCountInvalid
    name = msg[0]
    mode = msg[1]
    instance = await RandomLoot.with_map_name(name, mode)
    if instance is None:
        await RandomLootMatcher.finish(PROMPT.DungeonInvalid + "\n由于上游数据错误，暂时只可模拟25人英雄一之窟。")
    else:
        image = await instance.generate()
        await RandomLootMatcher.finish(ms.at(event.user_id) + image)