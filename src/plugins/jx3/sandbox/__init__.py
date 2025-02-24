from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent
)

from src.config import Config
from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.database.operation import get_group_settings

from .api import get_sandbox_image

SandboxMatcher = on_command("jx3_sandbox_v2", aliases={"沙盘v2", "沙盘"}, force_whitespace=True, priority=5)

@SandboxMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    获取服务器沙盘：
    Example：-沙盘v2 幽月轮
    """
    additions = get_group_settings(str(event.group_id), "additions")
    if not Config.jx3.api.enable and not "Preview" in additions:
        return
    if args.extract_plain_text() == "":
        """
        沙盘
        """
        server = Server(None, event.group_id).server
        if server is None:
            await SandboxMatcher.finish(PROMPT.ServerNotExist)
        image = await get_sandbox_image(server)
    else:
        """
        沙盘 服务器
        """
        server = Server(args.extract_plain_text(), event.group_id).server
        if server is None:
            await SandboxMatcher.finish(PROMPT.ServerNotExist)
        image = await get_sandbox_image(server)
    await SandboxMatcher.finish(image)