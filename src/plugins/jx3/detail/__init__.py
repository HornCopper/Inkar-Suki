from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageSegment as ms,
)
from nonebot.params import Arg, CommandArg
from nonebot.typing import T_State

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.database.player import search_player

from .detail import VIEW_TYPES, get_exp_info


achievement_overview_matcher = on_command(
    "jx3_exp", aliases={"资历分布"}, priority=5, force_whitespace=True
)


@achievement_overview_matcher.handle()
async def _(
    event: GroupMessageEvent,
    state: T_State,
    argument: Message = CommandArg(),
):
    args = argument.extract_plain_text().strip().split()
    if len(args) not in (1, 2):
        await achievement_overview_matcher.finish(
            PROMPT.ArgumentCountInvalid + "\n参考格式：资历分布 <服务器> <角色名>"
        )

    if len(args) == 1:
        server = Server(None, event.group_id).server
        role_name = args[0]
        if server is None:
            await achievement_overview_matcher.finish(PROMPT.ServerNotExist)
    else:
        server = Server(args[0], event.group_id).server
        role_name = args[1]
        if server is None:
            await achievement_overview_matcher.finish(PROMPT.ServerInvalid)

    state["role"] = (server, role_name)
    choices = "\n".join(
        f"{index}. {view}" for index, view in enumerate(VIEW_TYPES, start=1)
    )
    await achievement_overview_matcher.send(
        ms.at(event.user_id) + f" 请选择要查看的类型：\n{choices}"
    )


@achievement_overview_matcher.got("choice")
async def _(state: T_State, choice: Message = Arg()):
    selected = choice.extract_plain_text().strip()
    if selected not in {str(index) for index in range(1, len(VIEW_TYPES) + 1)}:
        await achievement_overview_matcher.finish(
            "给定的序号不正确，请重新发起命令！"
        )

    server, role_name = state["role"]
    player_data = await search_player(role_name=role_name, server_name=server)
    if not player_data.globalRoleId:
        await achievement_overview_matcher.finish(PROMPT.PlayerNotExist)

    result = await get_exp_info(
        server,
        role_name,
        player_data.globalRoleId,
        VIEW_TYPES[int(selected) - 1],
    )
    await achievement_overview_matcher.finish(result)
