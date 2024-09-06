from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.tools.permission import checker, error
from src.tools.utils.file import get_content_local

from src.plugins.sign import Sign

from .universe import (
    dj_calculator, # 毒经
    wf_calculator # 无方
)

from .wf import *

calc_dj = on_command("jx3_calculator_dj", aliases={"毒经计算器"}, priority=5) # 目前先对毒经的计算器进行响应，后续尽可能多地支持

@calc_dj.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await calc_dj.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await dj_calculator(server, id, str(event.group_id))
    if isinstance(data, list):
        await calc_dj.finish(data[0])
    elif isinstance(data, str):
        data = get_content_local(data)
        await calc_dj.finish(ms.image(data))

calc_wf = on_command("jx3_calculator_wf", aliases={"无方计算器"}, priority=5) # 目前先对无方的计算器进行响应，后续尽可能多地支持

@calc_wf.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await calc_wf.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    data = await wf_calculator(server, id, str(event.group_id))
    if isinstance(data, list):
        await calc_wf.finish(data[0])
    elif isinstance(data, str):
        data = get_content_local(data)
        await calc_wf.finish(ms.image(data))