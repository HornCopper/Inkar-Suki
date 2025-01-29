from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.permission import check_permission, denied

from .lxg import LingxueCalculator
from .zxg import ZixiagongCalculator
from .bxj import BingxinjueCalculator

YLJCalcMatcher = on_command("jx3_calculator_lyj", aliases={"凌雪计算器"}, priority=5, force_whitespace=True)

@YLJCalcMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await YLJCalcMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await YLJCalcMatcher.finish(PROMPT.ServerNotExist)
    instance = await LingxueCalculator.with_name(name, server)
    if isinstance(instance, str):
        await YLJCalcMatcher.finish(instance)
    data = await instance.image()
    await YLJCalcMatcher.finish(data)

ZXGCalculator = on_command("jx3_calculator_zxg", aliases={"气纯计算器"}, priority=5, force_whitespace=True)

@ZXGCalculator.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await ZXGCalculator.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await ZXGCalculator.finish(PROMPT.ServerNotExist)
    instance = await ZixiagongCalculator.with_name(name, server)
    if isinstance(instance, str):
        await ZXGCalculator.finish(instance)
    data = await instance.image()
    await ZXGCalculator.finish(data)

BXJCalculator = on_command("jx3_calculator_bxj", aliases={"冰心计算器"}, priority=5, force_whitespace=True)

@BXJCalculator.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if not check_permission(event.user_id, 1):
        await BXJCalculator.finish(denied(1))
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await BXJCalculator.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await BXJCalculator.finish(PROMPT.ServerNotExist)
    instance = await BingxinjueCalculator.with_name(name, server)
    if isinstance(instance, str):
        await BXJCalculator.finish(instance)
    data = await instance.image()
    await BXJCalculator.finish(data)