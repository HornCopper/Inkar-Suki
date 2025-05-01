from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent
)
from nonebot.params import CommandArg

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.const.jx3.dungeon import Dungeon

from .v2 import (
    get_progress_v2,
    zone_achievement
)

achievement_v2_matcher = on_command("jx3_progress_v2", aliases={"进度", "成就进度", "成就"}, force_whitespace=True, priority=5)

@achievement_v2_matcher.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    args = msg.extract_plain_text().split(" ")

    if len(args) not in [2, 3]:
        await achievement_v2_matcher.finish(PROMPT.ArgumentCountInvalid + "\n进度 <服务器> <角色名> <关键词>")

    if len(args) == 2:
        server = ""
        role_name = args[0]
        achievement_name = args[1]

    elif len(args) == 3:
        server = args[0]
        role_name = args[1]
        achievement_name = args[2]

    group_server = Server(server_name=server, group_id=event.group_id)

    if not group_server.server:
        await achievement_v2_matcher.finish(PROMPT.ServerNotExist)

    data = await get_progress_v2(group_server.server, role_name, achievement_name)
    await achievement_v2_matcher.finish(data)

zone_achievement_matcher = on_command("jx3_zoneachi", aliases={"团本成就"}, force_whitespace=True, priority=5)

@zone_achievement_matcher.handle()
async def _(event: GroupMessageEvent, full_argument: Message = CommandArg()):
    args = full_argument.extract_plain_text().split(" ")

    if len(args) not in [2, 3, 4]:
        await zone_achievement_matcher.finish(PROMPT.ArgumentCountInvalid + "\n团本成就 <服务器> <角色名> <副本名> [难度(默认10人)]")

    if len(args) == 2:
        """
        双参数：
        
        团本成就 ID DNAME
        """
        GroupServer = Server(group_id=event.group_id).server
        if not GroupServer:
            await zone_achievement_matcher.finish(PROMPT.ServerNotExist)
        DungeonName = Dungeon(args[1], "").name
        if not DungeonName:
            await zone_achievement_matcher.finish(PROMPT.DungeonNameInvalid)
        server = GroupServer
        role_name = args[0]
        zone = DungeonName
        mode = "10人普通"

    elif len(args) == 3:
        """
        三参数：

        团本成就 ID DNAME DMODE
        团本成就 SRV ID DNAME
        """
        server = Server(args[0]).server
        if not server:
            """
            三参数：

            团本成就 ID DNAME DMODE
            """
            server = Server(group_id=event.group_id).server
            if not server:
                await zone_achievement_matcher.finish(PROMPT.ServerNotExist)
            role_name = args[0]
            DungeonObj = Dungeon(args[1], args[2])
            zone, mode = DungeonObj.name, DungeonObj.mode
            if not zone or not mode:
                await zone_achievement_matcher.finish(PROMPT.DungeonInvalid)
        else:
            """
            三参数：

            团本成就 SRV ID DNAME
            """
            role_name = args[1]
            zone = Dungeon(args[2], "").name
            if not zone:
                await zone_achievement_matcher.finish(PROMPT.DungeonNameInvalid)
            mode = "10人普通"
            
    
    elif len(args) == 4:
        """
        四参数：

        团本成就 SRV ID DNAME DMODE
        """
        server = Server(args[0], event.group_id).server
        if not server:
            await zone_achievement_matcher.finish(PROMPT.ServerNotExist)
        role_name = args[1]
        DungeonObj = Dungeon(args[2], args[3])
        zone, mode = DungeonObj.name, DungeonObj.mode
        if not zone or not mode:
            await zone_achievement_matcher.finish(PROMPT.DungeonInvalid)

    data = await zone_achievement(server, role_name, zone, mode)
    await zone_achievement_matcher.finish(data)