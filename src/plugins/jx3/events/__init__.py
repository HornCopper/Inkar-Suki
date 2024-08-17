from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.tools.basic.data_server import server_mapping
from src.tools.basic.msg import PROMPT
from src.tools.file import get_content_local

from .chutian import *
from .yuncong import *
from .zhue import *

cts = on_command("jx3_chutian", aliases={"楚天社"}, force_whitespace=True, priority=5)

@cts.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    image = await getChutianImg()
    await cts.finish(ms.image(image))

ycs = on_command("jx3_yuncong", aliases={"云从社"}, force_whitespace=True, priority=5)

@ycs.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    image = await getYuncongImg()
    await ycs.finish(ms.image(image))

zhue_ = on_command("jx3_zhue", aliases={"诛恶"}, force_whitespace=True, priority=5)

@zhue_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    server = server_mapping(args.extract_plain_text(), str(event.group_id))
    if server == None:
        await zhue_.finish(PROMPT.ServerNotExist)
    else:
        img = get_content_local(await getZhueRecord(server))
        await zhue_.finish(ms.image(img))