from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from src.tools.basic.server import server_mapping
from src.tools.basic.prompts import PROMPT

from .api import *

cmd_jx3_server = on_command("jx3_server", aliases={"开服"}, priority=5, force_whitespace=True)

@cmd_jx3_server.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取服务器开服状态：

    Example：-服务器 幽月轮
    Example：-开服 幽月轮 
    """
    server = args.extract_plain_text()
    srv = server_mapping(server, str(event.group_id))
    if srv == None:
        await cmd_jx3_server.finish(PROMPT.ServerNotExist)
    msg = await server_status(srv)
    await cmd_jx3_server.finish(msg)