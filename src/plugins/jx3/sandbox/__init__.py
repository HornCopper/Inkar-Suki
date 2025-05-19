from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent
)

from src.config import Config
from src.const.jx3.server import Server
from src.const.prompts import PROMPT

from .api import get_sandbox_image

sandbox_matcher = on_command("jx3_sandbox_v2", aliases={"沙盘v2", "沙盘"}, force_whitespace=True, priority=5)

@sandbox_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取服务器沙盘：
    Example：-沙盘v2 幽月轮
    """
    if not Config.jx3.api.enable:
        return
    if args.extract_plain_text() == "":
        """
        沙盘
        """
        server = Server(None, event.group_id).server
        if server is None:
            await sandbox_matcher.finish(PROMPT.ServerNotExist)
        image = await get_sandbox_image(server)
    else:
        """
        沙盘 服务器
        """
        server = Server(args.extract_plain_text(), event.group_id).server
        if server is None:
            await sandbox_matcher.finish(PROMPT.ServerNotExist)
        image = await get_sandbox_image(server)
    await sandbox_matcher.finish(image)