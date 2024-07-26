from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg

from src.tools.basic.data_server import server_mapping
from src.tools.file import get_content_local
from src.tools.basic.msg import PROMPT

from .api import *

tz = on_command("jx3_tongzhan", aliases={"统战", "统战YY", "统战yy"})

@tz.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    server = server_mapping(args.extract_plain_text(), str(event.group_id))
    if server == None:
        await tz.finish(PROMPT.ServerNotExist)
    else:
        image = await getTongzhan(server)
        image = get_content_local(image)
        await tz.finish(ms.image(image))