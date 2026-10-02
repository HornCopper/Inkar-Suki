from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

from src.config import Config
from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.command import on_command
from src.utils.permission import check_group_permission

from .api import get_chat_records


chat_records_matcher = on_command("jx3_chat_records", command_key="聊天", aliases={"聊天", "发言"}, force_whitespace=True, priority=5)


@chat_records_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if not Config.jx3.api.enable or not check_group_permission(event.group_id, "group.application.chat_records"):
        return
    if args.extract_plain_text() == "":
        return

    arg = args.extract_plain_text().strip().split()
    explicit_server = Server(arg[0]).server if len(arg) >= 2 else None
    if explicit_server is None:
        server = Server(None, event.group_id).server
        name = arg[0]
        options = arg[1:]
    else:
        server = explicit_server
        name = arg[1]
        options = arg[2:]

    if server is None:
        await chat_records_matcher.finish(PROMPT.ServerNotExist)
    if len(options) > 2:
        await chat_records_matcher.finish(
            PROMPT.ArgumentCountInvalid
            + "\n参考格式：聊天 <服务器> <角色名> [页码] [每页数量]"
        )

    try:
        page = int(options[0]) if options else 1
        limit = int(options[1]) if len(options) == 2 else 20
    except ValueError:
        await chat_records_matcher.finish(PROMPT.NumberInvalid)
    if page < 1 or limit not in range(1, 51):
        await chat_records_matcher.finish(PROMPT.NumberInvalid)

    msg = await get_chat_records(server, name, page, limit)
    await chat_records_matcher.finish(msg)
