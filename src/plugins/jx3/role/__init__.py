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

from .api import get_role_info

RoleInfoMatcher = on_command("jx3_player", aliases={"玩家信息"}, force_whitespace=True, priority=5)

@RoleInfoMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    additions = get_group_settings(str(event.group_id), "additions")
    if not Config.jx3.api.enable and "Preview" not in additions:
        return
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await RoleInfoMatcher.finish("唔……参数不正确哦，请检查后重试~")
    if len(arg) == 1:
        server = None
        name = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await RoleInfoMatcher.finish(PROMPT.ServerNotExist)
    msg = await get_role_info(server, name)
    await RoleInfoMatcher.finish(msg)