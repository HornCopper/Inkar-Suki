from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.const.jx3.server import Server
from src.const.prompts import PROMPT

from .api import get_coin_price_image

CoinPriceMatcher = on_command("jx3_demon", aliases={"金价"}, force_whitespace=True, priority=5)


@CoinPriceMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取各服金价：

    Example：-金价 幽月轮
    """
    server = Server(args.extract_plain_text(), event.group_id).server
    if server is None:
        await CoinPriceMatcher.finish(PROMPT.ServerNotExist)
    data = await get_coin_price_image(server)
    await CoinPriceMatcher.finish(data)
