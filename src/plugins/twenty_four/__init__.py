from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.params import CommandArg, Received
from nonebot.typing import T_State

from src.accounts.manage import AccountManage

from .process import (
    find_solution, 
    check_valid, 
    calc, 
    contains_all_numbers
)

import random

TwentyFourMatcher = on_command("twentyFour", aliases={"24点"}, force_whitespace=True, priority=5)


@TwentyFourMatcher.handle()
async def _(state: T_State, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    numbers = [random.randint(1, 13) for _ in range(4)]
    state["numbers"] = numbers
    await TwentyFourMatcher.send(f"音卡翻出了这组数字：{numbers}\n请告诉我一个表达式，使其结果为 24。（若无解，可以告诉我“无解”）")
    return

@TwentyFourMatcher.receive("answer")
async def __(state: T_State, event: MessageEvent = Received("answer")):
    expr = str(event.message).replace("（", "(").replace("）", ")")
    numbers = state["numbers"]
    solution = await find_solution(numbers)
    if expr == "无解":
        if solution:
            AccountManage(event.user_id).reduce_coin(3100)
            await TwentyFourMatcher.finish(f"唔……回答错误，并非无解哦。\n其中一组解为：{solution}\n您失去了 3100 枚金币。")
        else:
            AccountManage(event.user_id).add_coin(5000)
            await TwentyFourMatcher.finish("回答正确！\n您获得了 5000 枚金币。")
    elif check_valid(expr):
        result = calc(expr)
        if not result:
            AccountManage(event.user_id).reduce_coin(3700)
            await TwentyFourMatcher.finish("唔……回答错误，您的表达式真的能算吗？\n您失去了 3700 枚金币。")
        elif (result == 24 or 0 < 24 - result < 1e-13 ) \
            and contains_all_numbers(expr, numbers):
            AccountManage(event.user_id).add_coin(5000)
            await TwentyFourMatcher.finish("回答正确！\n您获得了 5000 枚金币。")
        else:
            AccountManage(event.user_id).reduce_coin(3100)
            await TwentyFourMatcher.finish("唔……回答错误。\n您失去了 3100 枚金币。")
    else:
        AccountManage(event.user_id).reduce_coin(3700)
        await TwentyFourMatcher.finish("唔……回答错误，您的表达式真的能算吗？\n您失去了 3700 枚金币。")
