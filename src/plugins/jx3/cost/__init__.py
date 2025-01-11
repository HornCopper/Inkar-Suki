from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.permission import check_permission

from .processer import get_item_data, DataProcesser

CostCalculatorMatcher = on_command("成本", priority=5, force_whitespace=True)

@CostCalculatorMatcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    if argument.extract_plain_text() == "":
        return
    if not check_permission(event.user_id, 10):
        await CostCalculatorMatcher.finish("该功能内测中，敬请期待！")
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
    image = await DataProcesser(item_data).render_image(server)
    await CostCalculatorMatcher.finish(image)