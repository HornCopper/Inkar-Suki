from src.plugins.sign import Sign

from .process import *
from src.tools.basic import *

no_solution = ['无解', '無解', 'none', 'n/a']


tf = on_command("twentyFour", aliases={"24点"}, priority=5)


@tf.handle()
async def _(state: T_State, event: Event):
    numbers = [random.randint(1, 13) for _ in range(4)]
    state["numbers"] = numbers
    await tf.send(f"给出的数字组合：{numbers}\n请输入表达式使其结果为24。（若无解，请输入“无解”）")
    return

@tf.receive("answer")
async def __(state: T_State, event: Event = Received("answer")):
    expr = str(event.message)
    numbers = state["numbers"]
    solution = await find_solution(numbers)
    if expr = '无解':
        if solution:
            Sign.reduce(str(event.user_id), 50)
            await tf.finish(f"回答错误：该组合存在解。\n其中一组解为：{solution}\n您失去了50枚金币。")
        else:
            Sign.add(str(event.user_id), 50)
            await tf.finish("回答正确。\n您获得了50枚金币。")
    elif check_valid(expr):
        result = calc(expr)
        if not result:
            await tf.finish("回答错误：表达式无效。")
        elif (result == 24 or 0 < 24 - result < 1e-13 ) \
            and contains_all_numbers(expr, numbers):
            Sign.add(str(event.user_id), 50)
            await tf.finish("回答正确。\n您获得了50枚金币。")
        else:
            await tf.finish("回答错误。")
    else:
        await tf.finish("回答错误：表达式无效。")