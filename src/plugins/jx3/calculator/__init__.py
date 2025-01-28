from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.const.prompts import PROMPT
from src.const.jx3.server import Server

from .lxg import LingxueCalculator

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
    data = await (await LingxueCalculator.with_name(name, server)).image()
    await YLJCalcMatcher.finish(data)