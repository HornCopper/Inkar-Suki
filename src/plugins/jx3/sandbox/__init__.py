from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.tools.basic.server import server_mapping
from src.tools.utils.file import get_content_local

from .api import *

sandbox_v2 = on_command("jx3_sandbox_v2", aliases={"沙盘v2", "沙盘"}, force_whitespace=True, priority=5)

@sandbox_v2.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取服务器沙盘：
    Example：-沙盘v2 幽月轮
    """
    server = args.extract_plain_text()
    server_ = server_mapping(server, str(event.group_id))
    data = await sandbox_v2_(server_)
    if isinstance(data, list):
        await sandbox_v2.finish(data[0])
    elif isinstance(data, str):
        data = get_content_local(data)
        await sandbox_v2.finish(ms.image(data))