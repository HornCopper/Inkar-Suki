from typing import List

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State
from nonebot.matcher import Matcher

from src.const.prompts import PROMPT
from src.utils.analyze import check_number
from src.utils.network import Request
from src.const.jx3.server import Server
from src.const.jx3.dungeon import Dungeon

from .box import (
    get_adventure,
    AchievementInformation
)
from .v2 import (
    get_progress_v2,
    zone_achievement
)

JX3AdventureMatcher = on_command(
    "jx3_adventure",
    aliases={"成就"},
    force_whitespace=True,
    priority=5
)

@JX3AdventureMatcher.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    full_argument: Message = CommandArg()
):
    """
    查询成就信息：

    Example：-成就 好久不见
    """
    if full_argument.extract_plain_text() == "":
        matcher.stop_propagation()
        return
    achievement_name = full_argument.extract_plain_text()
    data = await get_adventure(achievement_name)
    if not data:
        return [PROMPT.AchievementNotFound]
    else:
        if len(data) == 1:
            # 最佳匹配
            image_url = data[0].icon
            image = (await Request(image_url).get()).content
            msg = f"查询到「{data[0].name}」：\n{ms.image(image)}\n{data[0].sip_desc}\n{data[0].full_desc}\n地图：{data[0].map}\n资历：{data[0].point}点"
            await JX3AdventureMatcher.finish(msg)
        else:
            if len(data) > 20:
                data = data[:20]
            state["v"] = data
            msg = "音卡找到下面的相关成就，请回复前方序号来搜索！"
            for num, information in enumerate(data, start=1):
                msg += f"\n{num}. {information.name}"
            await JX3AdventureMatcher.send(msg)

@JX3AdventureMatcher.got("num")
async def _(
    state: T_State,
    num: Message = Arg()
):
    num_ = num.extract_plain_text()
    data: List[AchievementInformation] = state["v"]
    if check_number(num_) and int(num_) <= len(data):
        image_url = data[int(num_)].icon
        image = (await Request(image_url).get()).content
        msg = f"查询到「{data[int(num_) - 1].name}」：\n{ms.image(image)}\n{data[int(num_)].sip_desc}\n{data[int(num_)].full_desc}\n地图：{data[int(num_)].map}\n资历：{data[int(num_)].point}点"
        await JX3AdventureMatcher.finish(msg)
    else:
        await JX3AdventureMatcher.finish(PROMPT.NumberInvalid)

JX3ProgressV2Matcher = on_command(
    "jx3_progress_v2", 
    aliases={"进度"}, 
    force_whitespace=True, 
    priority=5
)

@JX3ProgressV2Matcher.handle()
async def _(
    event: GroupMessageEvent, 
    full_argument: Message = CommandArg()
):
    args = full_argument.extract_plain_text().split(" ")

    if len(args) not in [2, 3]:
        await JX3ProgressV2Matcher.finish(PROMPT.ArgumentCountInvalid)

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
        await JX3ProgressV2Matcher.finish(PROMPT.ServerNotExist)

    data = await get_progress_v2(group_server.server, role_name, achievement_name)
    if isinstance(data, list):
        await JX3ProgressV2Matcher.finish(data[0])
    elif isinstance(data, str):
        data = Request(data).local_content
        await JX3ProgressV2Matcher.finish(ms.image(data))

ZoneAchiMatcher = on_command("jx3_zoneachi", aliases={"团本成就"}, force_whitespace=True, priority=5)

@ZoneAchiMatcher.handle()
async def _(event: GroupMessageEvent, full_argument: Message = CommandArg()):
    args = full_argument.extract_plain_text().split(" ")

    if len(args) not in [2, 3, 4]:
        await ZoneAchiMatcher.finish(PROMPT.ArgumentCountInvalid)

    if len(args) == 2:
        """
        双参数：
        
        团本成就 ID DNAME
        """
        GroupServer = Server(group_id=event.group_id).server
        if not GroupServer:
            await ZoneAchiMatcher.finish(PROMPT.ServerNotExist)
        DungeonName = Dungeon(args[1], "").name
        if not DungeonName:
            await ZoneAchiMatcher.finish(PROMPT.DungeonNameInvalid)
        server = GroupServer
        id = args[0]
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
                await ZoneAchiMatcher.finish(PROMPT.ServerNotExist)
            id = args[0]
            DungeonObj = Dungeon(args[1], args[2])
            zone, mode = DungeonObj.name, DungeonObj.mode
            if not zone or not mode:
                await ZoneAchiMatcher.finish(PROMPT.DungeonInvalid)
        else:
            """
            三参数：

            团本成就 SRV ID DNAME
            """
            id = args[1]
            zone = Dungeon(args[2], "").name
            if not zone:
                await ZoneAchiMatcher.finish(PROMPT.DungeonNameInvalid)
            mode = "10人普通"
            
    
    elif len(args) == 4:
        """
        四参数：

        团本成就 SRV ID DNAME DMODE
        """
        server = Server(args[0], event.group_id).server
        if not server:
            await ZoneAchiMatcher.finish(PROMPT.ServerNotExist)
        id = args[1]
        DungeonObj = Dungeon(args[2], args[3])
        zone, mode = DungeonObj.name, DungeonObj.mode
        if not zone or not mode:
            await ZoneAchiMatcher.finish(PROMPT.DungeonInvalid)

    data = await zone_achievement(server, id, zone, mode)
    if isinstance(data, list):
        await ZoneAchiMatcher.finish(data[0])
    else:
        if not isinstance(data, str):
            return
        data = Request(data).local_content
        await ZoneAchiMatcher.finish(ms.image(data))