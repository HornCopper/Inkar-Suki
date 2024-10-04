from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.network import Request

from .v2 import get_attr_v2
from .v4 import get_attrs_v4

AttributeV2Matcher = on_command("jx3_addritube_v2", aliases={"属性", "查装", "属性v2", "查装v2"}, force_whitespace=True, priority=5)

@AttributeV2Matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询某玩家的装备：

    Example：-属性 幽月轮 哭包猫@唯我独尊
    Example：-查装 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await AttributeV2Matcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    ServerInstance = Server(server, event.group_id)
    if not ServerInstance.server:
        await AttributeV2Matcher.finish(PROMPT.ServerNotExist)
    data = await get_attr_v2(ServerInstance.server, id)
    if isinstance(data, list):
        await AttributeV2Matcher.finish(data[0])
    else:
        data = Request(data).local_content
        await AttributeV2Matcher.finish(ms.image(data))

AttributeV4Matcher = on_command("jx3_addritube_v4", aliases={"属性v4", "查装v4"}, force_whitespace=True, priority=5)

@AttributeV4Matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询某玩家的装备：

    Example：-属性v4 幽月轮 哭包猫@唯我独尊
    Example：-查装v4 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await AttributeV4Matcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    ServerInstance = Server(server, event.group_id)
    if not ServerInstance.server:
        await AttributeV2Matcher.finish(PROMPT.ServerNotExist)
    data = await get_attrs_v4(ServerInstance.server, id)
    if isinstance(data, list):
        await AttributeV4Matcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await AttributeV4Matcher.finish(ms.image(data))