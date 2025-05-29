from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.const.prompts import PROMPT
from src.const.jx3.dungeon import Dungeon
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.server import Server
from src.const.jx3.school import School

from .api import get_zlrank
from .rank import get_rank, get_slrank

exp_rank_matcher = on_command("jx3_zlrank", aliases={"资历排行", "资历榜单"}, priority=5, force_whitespace=True)

@exp_rank_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [0, 1, 2]:
        await exp_rank_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：资历排行 [服务器] [门派]")
    if args[0] == "":
        """
        CMD
        """
        server = ""
        school = ""
        if server is None:
            await exp_rank_matcher.finish(PROMPT.ServerNotExist)
    elif len(args) == 1:
        """
        CMD SCH/SRV
        """
        if Server(args[0], None).server is None:
            """
            CMD SCH
            """
            school = School(args[0]).name or ""
            server = ""
        else:
            """
            CMD SRV
            """
            school = ""
            server = Server(args[0], None).server or ""
    elif len(args) == 2:
        server = Server(args[0], event.group_id).server or ""
        school = School(args[1]).name or ""
    image = await get_zlrank(server, school)
    await exp_rank_matcher.finish(image)

rdps_rank_matcher = on_command("jx3_rdps_rank", aliases={"RD天梯"}, priority=5)

rhps_rank_matcher = on_command("jx3_rhps_rank", aliases={"RH天梯"}, priority=5)

@rdps_rank_matcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if msg.extract_plain_text() == "":
        return
    args = msg.extract_plain_text().strip().split(" ")
    if len(args) != 4:
        await rdps_rank_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：RD天梯 <副本名> <副本难度> <首领名> <心法名>")
    _dungeon_name = args[0]
    _dungeon_mode = args[1]
    boss_name = args[2]
    _kungfu_name = args[3]
    dungeon = Dungeon(_dungeon_name, _dungeon_mode)
    dungeon_name, dungeon_mode = dungeon.name, dungeon.mode
    kungfu_name = Kungfu(_kungfu_name).name
    inject_msg = ""
    if not dungeon_name or not dungeon_mode:
        inject_msg = PROMPT.DungeonInvalid
    if not kungfu_name:
        inject_msg = PROMPT.KungfuNotExist
    if inject_msg:
        await rdps_rank_matcher.finish(inject_msg)
    reply_msg = await get_rank(str(dungeon_mode) + str(dungeon_name), boss_name, str(kungfu_name), "rdps")
    await rdps_rank_matcher.finish(reply_msg)

@rhps_rank_matcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if msg.extract_plain_text() == "":
        return
    args = msg.extract_plain_text().strip().split(" ")
    if len(args) != 4:
        await rhps_rank_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：RH天梯 <副本名> <副本难度> <首领名> <心法名>")
    _dungeon_name = args[0]
    _dungeon_mode = args[1]
    boss_name = args[2]
    _kungfu_name = args[3]
    dungeon = Dungeon(_dungeon_name, _dungeon_mode)
    dungeon_name, dungeon_mode = dungeon.name, dungeon.mode
    kungfu_name = Kungfu(_kungfu_name).name
    inject_msg = ""
    if not dungeon_name or not dungeon_mode:
        inject_msg = PROMPT.DungeonInvalid
    if not kungfu_name:
        inject_msg = PROMPT.KungfuNotExist
    if inject_msg:
        await rhps_rank_matcher.finish(inject_msg)
    reply_msg = await get_rank(str(dungeon_mode) + str(dungeon_name), boss_name, str(kungfu_name), "rhps")
    await rhps_rank_matcher.finish(reply_msg)

slrank_matcher = on_command("jx3_slrank", aliases={"试炼之地", "试炼"}, priority=5, force_whitespace=True)

@slrank_matcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if msg.extract_plain_text() == "":
        return
    args = msg.extract_plain_text().strip().split(" ")
    if len(args) not in [1, 2]:
        await slrank_matcher.finish(PROMPT.ArgumentCountInvalid)
    if len(args) == 1:
        server = Server(None, event.group_id).server
        school = args[0]
    if len(args) == 2:
        if args[0] != "全服":
            server = Server(args[0], event.group_id).server
        else:
            server = "全服"
        school = args[1]
    school = School(school).name
    if school is None:
        await slrank_matcher.finish(PROMPT.SchoolInvalid)
    if server is None:
        await slrank_matcher.finish(PROMPT.ServerNotExist)
    reply_msg = await get_slrank(school, server)
    await slrank_matcher.finish(reply_msg)