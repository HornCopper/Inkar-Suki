from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment as ms

from src.config import Config
from src.const.prompts import PROMPT
from src.utils.network import Request

from .random_loot import RandomLoot

saohua_matcher = on_command("jx3_random", aliases={"骚话", "烧话"}, force_whitespace=True, priority=5)

@saohua_matcher.handle()
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
    await saohua_matcher.finish(msg)

tiangou_matcher = on_command("jx3_tiangou", aliases={"舔狗", "舔狗日记"}, force_whitespace=True, priority=5)

@tiangou_matcher.handle()
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
    await tiangou_matcher.finish(msg)

random_loot_matcher = on_command("jx3_rdloot", aliases={"黑本", "模拟掉落", "红本"}, force_whitespace=True, priority=5)

@random_loot_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg == "":
        return
    msg = msg.split(" ")
    if len(msg) != 2:
        await random_loot_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：黑本 <副本名> <难度>")
    name = msg[0]
    mode = msg[1]
    instance = await RandomLoot.with_map_name(name, mode)
    if instance is None:
        await random_loot_matcher.finish(PROMPT.DungeonInvalid)
    else:
        image = await instance.generate()
        await random_loot_matcher.finish(ms.at(event.user_id) + image)