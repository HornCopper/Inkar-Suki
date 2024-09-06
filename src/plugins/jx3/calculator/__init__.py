from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.tools.permission import checker, error
from src.tools.utils.file import get_content_local

from src.plugins.sign import Sign

from .universe import (
    dj_calculator
)

calc = on_command("jx3_calculator_dj", aliases={"毒经计算器"}, priority=5) # 目前先对毒经的计算器进行响应，后续尽可能多地支持

@calc.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    # if not checker(str(event.user_id), 10) and Sign.get_coin(str(event.user_id)) < 500:
    #     await calc.finish(error(10))
    # if not checker(str(event.user_id), 10):
    #     Sign.reduce(str(event.user_id), 500)
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await calc.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await dj_calculator(server, id, str(event.group_id))
    if isinstance(data, list):
        await calc.finish(data[0])
    elif isinstance(data, str):
        data = get_content_local(data)
        await calc.finish(ms.image(data))