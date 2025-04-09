from nonebot import on_command
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.analyze import check_number
from src.utils.network import Request

from .processer import get_item_data, JX3CostCalc

CostCalculatorMatcher = on_command("成本", priority=5, force_whitespace=True)

@CostCalculatorMatcher.handle()
async def _(event: GroupMessageEvent, state: T_State, argument: Message = CommandArg()):
    if argument.extract_plain_text() == "":
        return
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await CostCalculatorMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(args) == 1:
        server = None
        name = args[0]
    elif len(args) == 2:
        server = args[0]
        name = args[1]
    server = Server(server, event.group_id).server
    if server is None:
        await CostCalculatorMatcher.finish(PROMPT.ServerNotExist)
    item_data = await get_item_data(name)
    if not item_data:
        await CostCalculatorMatcher.finish("未找到该物品，请检查后重试！")
    if isinstance(item_data, list):
        msg = "音卡找到下面的相关物品，请回复前方序号来搜索！"
        state["d"] = item_data
        state["s"] = server
        for num, name in enumerate(item_data, start=1):
            n, _ = next(iter(name.items()))
            msg += f"\n[{num}] {n}"
            if num == 20:
                break
        await CostCalculatorMatcher.send(msg)
    else:
        image = await JX3CostCalc(item_data, server).render_image()
        await CostCalculatorMatcher.finish(image)

@CostCalculatorMatcher.got("num")
async def _(event: GroupMessageEvent, state: T_State, num: Message = Arg()):
    num_ = num.extract_plain_text()
    data: list[dict[str, str]] = state["d"]
    server: str = state["s"]
    if not check_number(num_):
        await CostCalculatorMatcher.finish("唔……输入的不是数字，取消搜索。")
    if int(num_) > len(data):
        await CostCalculatorMatcher.finish("唔……不存在该数字对应的搜索结果，请重新搜索！")
    name_with_url = data[int(num_)-1]
    _, url = next(iter(name_with_url.items()))
    image = await JX3CostCalc((await Request(url).get()).json(), server).render_image()
    await CostCalculatorMatcher.finish(image)