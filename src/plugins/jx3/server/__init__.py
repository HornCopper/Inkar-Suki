from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from src.const.prompts import PROMPT
from src.const.jx3.server import Server

from .api import get_server_status

ServerMatcher = on_command("jx3_server", aliases={"开服"}, priority=5, force_whitespace=True)

@ServerMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取服务器开服状态：

    Example：-服务器 幽月轮
    Example：-开服 幽月轮 
    """
    server = Server(args.extract_plain_text(), event.group_id).server
    if server is None:
        await ServerMatcher.finish(PROMPT.ServerNotExist)
    msg = await get_server_status(server)
    await ServerMatcher.finish(msg)