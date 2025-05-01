from nonebot import on_command
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment as ms

from src.utils.analyze import check_number
from src.const.prompts import PROMPT

from .dh import get_dh
from .wg import get_wg

dunhao_matcher = on_command("jx3_dh", aliases={"蹲号"}, force_whitespace=True, priority=5)

@dunhao_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    details = args.extract_plain_text()
    if details == "":
        await dunhao_matcher.finish(PROMPT.NoCondition)
    details = details.split(" ")
    if len(details) < 1:
        await dunhao_matcher.finish(PROMPT.NoCondition)
    final_details = ",".join(details)
    data = await get_dh(final_details)
    if isinstance(data, list):
        image = data[0]
        if not isinstance(image, str):
            matcher.stop_propagation()
            return
        state["links"] = data[1]
        state["floors"] = data[2]
        await dunhao_matcher.send(ms.image(image))
        return
    else:
        await dunhao_matcher.finish(data)

@dunhao_matcher.got("num", prompt="回复标题前方的序号，音卡就可以给你链接啦！")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num_ = num.extract_plain_text()
    if not check_number(num_):
        await dunhao_matcher.finish(PROMPT.NumberInvalid)
    else:
        links = state["links"]
        floors = state["floors"]
        floor = str(floors[int(num_)-1])
        await dunhao_matcher.finish(links[int(num_)-1] + f"\n请前往{floor}楼哦~")

waiguan_matcher = on_command("jx3_wg", aliases={"贴吧物价"}, force_whitespace=True, priority=5)

@waiguan_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    details = args.extract_plain_text()
    if details == "":
        await waiguan_matcher.finish(PROMPT.NoCondition)
    details = details.split(" ")
    if len(details) < 1:
        await waiguan_matcher.finish(PROMPT.NoCondition)
    final_details = ",".join(details)
    data = await get_wg(final_details)
    if isinstance(data, list):
        image = data[0]
        if not isinstance(image, str):
            matcher.stop_propagation()
            return
        state["links"] = data[1]
        state["floors"] = data[2]
        await waiguan_matcher.send(ms.image(image))
        return
    else:
        await waiguan_matcher.finish(data)

@waiguan_matcher.got("num", prompt="回复标题前方的序号，音卡就可以给你链接啦！")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num_ = num.extract_plain_text()
    if not check_number(num_):
        await waiguan_matcher.finish(PROMPT.NumberInvalid)
    else:
        links = state["links"]
        floors = state["floors"]
        floor = str(floors[int(num_)-1])
        await waiguan_matcher.finish(links[int(num_)-1] + f"\n请前往{floor}楼哦~")