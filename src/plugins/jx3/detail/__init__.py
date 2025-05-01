from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.database.player import search_player

from .detail import get_exp_info

VIEW_TYPES = [
    "全局总览",
    "地图总览",
    "五甲总览",
    "全局总览(含五甲)",
    "秘境总览"
]

achievement_overview_matcher = on_command("jx3_exp", aliases={"资历分布"}, priority=5, force_whitespace=True)

@achievement_overview_matcher.handle()
async def _(event: GroupMessageEvent, state: T_State, argument: Message = CommandArg()):
    if argument.extract_plain_text() == "":
        return
    args = argument.extract_plain_text().strip().split()
    if len(args) not in [1, 2]:
        await achievement_overview_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：资历分布 <服务器> <角色名>")
    if len(args) == 1:
        """
        CMD ID
        """
        server = Server(None, event.group_id).server
        role_name = args[0]
        if server is None:
            await achievement_overview_matcher.finish(PROMPT.ServerNotExist)
    elif len(args) == 2:
        server = Server(args[0], event.group_id).server
        role_name = args[1]
        if server is None:
            await achievement_overview_matcher.finish(PROMPT.ServerInvalid)
    
    state["r"] = (server, role_name)

    msg = "请选择要查看的类型："
    for num, type_name in enumerate(VIEW_TYPES, start=1):
        msg += f"\n{num}. {type_name}"

    await achievement_overview_matcher.send(ms.at(event.user_id) + f" {msg}")

@achievement_overview_matcher.got("choice")
async def _(event: GroupMessageEvent, state: T_State, choice: Message = Arg()):
    num = choice.extract_plain_text().strip()
    if num not in [str(n) for n in list(range(len(VIEW_TYPES) + 1))[1:]]:
        await achievement_overview_matcher.finish("给定的序号不正确，请重新发起命令！")
    role_info: tuple[str, str] = state["r"]
    server, role = role_info
    player_data = (await search_player(role_name=role, server_name=server)).format_jx3api()
    if player_data["code"] != 200:
        await achievement_overview_matcher.finish(PROMPT.PlayerNotExist)
    msg = await get_exp_info(server, role, player_data["data"]["globalRoleId"], VIEW_TYPES[int(num)-1])
    if isinstance(msg, ms):
        await achievement_overview_matcher.finish(msg)