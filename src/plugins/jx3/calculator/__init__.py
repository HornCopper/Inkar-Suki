from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.network import Request

from .universe import (
    dj_calculator, # 毒经
    wf_calculator, # 无方
    ylj_calculator, # 隐龙诀
    shxj_calculator, # 山海心诀
    zxg_calculator, # 紫霞功
)

DJCalcMatcher = on_command("jx3_calculator_dj", aliases={"毒经计算器"}, priority=5, force_whitespace=True) # 目前先对毒经的计算器进行响应，后续尽可能多地支持

@DJCalcMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await DJCalcMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    serverInstance = Server(server, event.group_id)
    if not serverInstance.server:
        await DJCalcMatcher.finish(PROMPT.ServerNotExist)
    data = await dj_calculator(serverInstance.server, id)
    if isinstance(data, list):
        await DJCalcMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await DJCalcMatcher.finish(ms.image(data))

WFCalcMatcher = on_command("jx3_calculator_wf", aliases={"无方计算器"}, priority=5, force_whitespace=True) # 目前先对无方的计算器进行响应，后续尽可能多地支持

@WFCalcMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await WFCalcMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    serverInstance = Server(server, event.group_id)
    if not serverInstance.server:
        await WFCalcMatcher.finish(PROMPT.ServerNotExist)
    data = await wf_calculator(serverInstance.server, id)
    if isinstance(data, list):
        await WFCalcMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await WFCalcMatcher.finish(ms.image(data))

YLJCalcMatcher = on_command("jx3_calculator_lyj", aliases={"凌雪计算器"}, priority=5, force_whitespace=True) # 目前先对凌雪阁的计算器进行响应，后续尽可能多地支持

@YLJCalcMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await YLJCalcMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    serverInstance = Server(server, event.group_id)
    if not serverInstance.server:
        await YLJCalcMatcher.finish(PROMPT.ServerNotExist)
    data = await ylj_calculator(serverInstance.server, id)
    if isinstance(data, list):
        await YLJCalcMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await YLJCalcMatcher.finish(ms.image(data))

SHXJCalcMatcher = on_command("jx3_calculator_shxj", aliases={"万灵计算器"}, priority=5, force_whitespace=True) # 目前先对万灵的计算器进行响应，后续尽可能多地支持

@SHXJCalcMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await SHXJCalcMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    serverInstance = Server(server, event.group_id)
    if not serverInstance.server:
        await SHXJCalcMatcher.finish(PROMPT.ServerNotExist)
    data = await shxj_calculator(serverInstance.server, id)
    if isinstance(data, list):
        await SHXJCalcMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await SHXJCalcMatcher.finish(ms.image(data))

ZXGCalcMatcher = on_command("jx3_calculator_zxg", aliases={"气纯计算器"}, priority=5, force_whitespace=True) # 目前先对紫霞功的计算器进行响应，后续尽可能多地支持

@ZXGCalcMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await ZXGCalcMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    serverInstance = Server(server, event.group_id)
    if not serverInstance.server:
        await ZXGCalcMatcher.finish(PROMPT.ServerNotExist)
    data = await zxg_calculator(serverInstance.server, id)
    if isinstance(data, list):
        await ZXGCalcMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await ZXGCalcMatcher.finish(ms.image(data))