from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.network import Request

from .v1 import get_preposition # v1 deleted
from .v2 import get_serendipity_v2 as v2_serendipity
from .v3 import get_serendipity_image_v3 as v3_serendipity

V2SerendipityMatcher = on_command("jx3_serendipity_v2", aliases={"奇遇v2", "查询v2"}, force_whitespace=True, priority=5)

@V2SerendipityMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取个人奇遇记录：

    Example：-奇遇v2 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await V2SerendipityMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await V2SerendipityMatcher.finish(PROMPT.ServerNotExist)
    data = await v2_serendipity(server, name, True)
    if isinstance(data, list):
        await V2SerendipityMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await V2SerendipityMatcher.finish(ms.image(data))

V3SerendipityMatcher = on_command("jx3_serendipity_v3", aliases={"奇遇v3", "查询v3", "奇遇", "查询"}, force_whitespace=True, priority=5)

@V3SerendipityMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取个人奇遇记录：

    Example：-奇遇v3 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await V3SerendipityMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await V3SerendipityMatcher.finish(PROMPT.ServerNotExist)
    data = await v3_serendipity(server, id)
    if isinstance(data, list):
        await V3SerendipityMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await V3SerendipityMatcher.finish(ms.image(data))

PetSerendipityMatcher = on_command("jx3_pet_serendipity", aliases={"宠物奇遇"}, force_whitespace=True, priority=5)

@PetSerendipityMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取个人奇遇记录：

    Example：-奇遇v2 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await PetSerendipityMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await PetSerendipityMatcher.finish(PROMPT.ServerNotExist)
    data = await v2_serendipity(server, name, False)
    if isinstance(data, list):
        await PetSerendipityMatcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await PetSerendipityMatcher.finish(ms.image(data))

PrepositionMatcher = on_command("jx3_preposition", aliases={"前置", "攻略"}, force_whitespace=True, priority=5)

@PrepositionMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    serendipity = args.extract_plain_text()
    data = await get_preposition(serendipity)
    if not data:
        await PrepositionMatcher.finish("唔……没有找到相关信息~")
    else:
        await PrepositionMatcher.finish(data)