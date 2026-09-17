from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent,
    MessageSegment as ms
)

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.command import on_command

from .api import get_role_info, get_online_info

role_info_matcher = on_command("jx3_player", command_key="玩家", aliases={"玩家信息", "玩家"}, force_whitespace=True, priority=5)

@role_info_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await role_info_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：玩家信息 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    else:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await role_info_matcher.finish(PROMPT.ServerNotExist)
    msg = await get_role_info(server, name)
    await role_info_matcher.finish(msg)

online_matcher = on_command("jx3_online", command_key="在线", aliases={"在线", "查在线"}, force_whitespace=True, priority=5)

@online_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await role_info_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：在线 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        name = arg[0]
    else:
        server = arg[0]
        name = arg[1]
    server = Server(server, event.group_id).server
    if server is None:
        await role_info_matcher.finish(PROMPT.ServerNotExist)
    msg = await get_online_info(server, name)
    await role_info_matcher.finish(msg)