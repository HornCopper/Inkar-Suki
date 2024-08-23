from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg, Received
from nonebot.typing import T_State

from src.plugins.sign import Sign

from .process import *

import random

tf = on_command("twentyFour", aliases={"24点"}, force_whitespace=True, priority=5)


@tf.handle()
async def _(state: T_State, event: MessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    numbers = [random.randint(1, 13) for _ in range(4)]
    state["numbers"] = numbers
    await tf.send(f"音卡翻出了这组数字：{numbers}\n请告诉我一个表达式，使其结果为24。（若无解，可以告诉我“无解”）")
    return

@tf.receive("answer")
async def __(state: T_State, event: MessageEvent = Received("answer")):
    expr = str(event.message)
    numbers = state["numbers"]
    solution = await find_solution(numbers)
    if expr == "无解":
        if solution:
            Sign.reduce(str(event.user_id), 50)
            await tf.finish(f"唔……回答错误，并非无解哦。\n其中一组解为：{solution}\n您失去了50枚金币。")
        else:
            Sign.add(str(event.user_id), 50)
            await tf.finish("回答正确！\n您获得了50枚金币。")
    elif check_valid(expr):
        result = calc(expr)
        if not result:
            await tf.finish("唔……回答错误，您的表达式真的能算吗？")
        elif (result == 24 or 0 < 24 - result < 1e-13 ) \
            and contains_all_numbers(expr, numbers):
            Sign.add(str(event.user_id), 50)
            await tf.finish("回答正确！\n您获得了50枚金币。")
        else:
            await tf.finish("唔……回答错误。")
    else:
        await tf.finish("唔……回答错误，您的表达式真的能算吗？")
