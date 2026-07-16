from typing import Any
from datetime import datetime

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.database import serendipity_db
from src.utils.database.classes import SerendipityData
from src.plugins.preferences.app import Preference

from .v1 import get_preposition # v1 deleted
from .v2 import get_serendipity_v2 as v2_serendipity
from .v3 import get_serendipity_image_v3 as v3_serendipity
from .v4 import get_serendipity_image_v4 as v4_serendipity
from .recent import get_recent_serendipity
from .statistics import get_serendipity_statistics
from .collect import get_serendipity_collect


collect_serendipity_matcher = on_command("jx3_collect_serendipity", aliases={"奇遇汇总", "汇总"}, force_whitespace=True, priority=5)


@collect_serendipity_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    args = argument.extract_plain_text().strip().split()
    if args and args[0] == "全服":
        await collect_serendipity_matcher.finish("奇遇汇总不支持全服查询，请指定服务器！")
    server = Server(None, event.group_id).server
    days = 7
    if len(args) == 1:
        if args[0].isdigit():
            days = int(args[0])
        else:
            server = Server(args[0]).server
    elif len(args) == 2:
        server = Server(args[0]).server
        if not args[1].isdigit():
            await collect_serendipity_matcher.finish(PROMPT.ArgumentInvalid)
        days = int(args[1])
    elif len(args) > 2:
        await collect_serendipity_matcher.finish(
            PROMPT.ArgumentCountInvalid + "\n参考格式：奇遇汇总 <服务器> [天数]"
        )
    if server is None:
        await collect_serendipity_matcher.finish(PROMPT.ServerNotExist)
    if not 1 <= days <= 30:
        await collect_serendipity_matcher.finish("汇总天数需要在 1 至 30 天之间！")
    image = await get_serendipity_collect(server, days)
    await collect_serendipity_matcher.finish(image)


statistics_serendipity_matcher = on_command("jx3_statistics_serendipity", aliases={"奇遇统计", "统计"}, force_whitespace=True, priority=5)


@statistics_serendipity_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    args = argument.extract_plain_text().strip().split(maxsplit=1)
    if len(args) == 1:
        server = Server(None, event.group_id).server
        event_name = args[0]
    elif len(args) == 2:
        server = "" if args[0] == "全服" else Server(args[0]).server
        event_name = args[1]
    else:
        await statistics_serendipity_matcher.finish(
            PROMPT.ArgumentCountInvalid + "\n参考格式：统计 <服务器> <奇遇名称>"
        )
    if server is None:
        await statistics_serendipity_matcher.finish(PROMPT.ServerNotExist)
    image = await get_serendipity_statistics(server, event_name)
    await statistics_serendipity_matcher.finish(image)


recent_serendipity_matcher = on_command("jx3_recent_serendipity", aliases={"近期奇遇"}, force_whitespace=True, priority=5)


@recent_serendipity_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    server_name = argument.extract_plain_text().strip() or None
    server = Server(server_name).server if server_name else Server(None, event.group_id).server
    if server is None:
        await recent_serendipity_matcher.finish(PROMPT.ServerNotExist)
    image = await get_recent_serendipity(server)
    await recent_serendipity_matcher.finish(image)

serendipity_matcher = on_command("jx3_serendipity", aliases={"查询", "奇遇"}, force_whitespace=True, priority=5)

@serendipity_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    if argument.extract_plain_text() == "":
        return
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await serendipity_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：查询 <服务器> <角色名>")
    if len(args) == 1:
        """
        查询 ID
        """
        server = None
        name = args[0]
    else:
        """
        查询 SRV ID
        """
        server = args[0]
        name = args[1]
    server = Server(server, event.group_id).server
    if server is None:
        await serendipity_matcher.finish(PROMPT.ServerNotExist)
    ver = Preference(event.user_id, "", "").setting("奇遇")
    if ver == "v2":
        data = await v2_serendipity(server, name, True)
    elif ver == "v4":
        data = await v4_serendipity(server, name)
    else:
        data = await v3_serendipity(server, name)
    await serendipity_matcher.finish(data)

serendipity_v2_matcher = on_command("jx3_serendipity_v2", aliases={"奇遇v2", "查询v2"}, force_whitespace=True, priority=5)

@serendipity_v2_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    if argument.extract_plain_text() == "":
        return
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await serendipity_v2_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：查询v2 <服务器> <角色名>")
    if len(args) == 1:
        """
        查询 ID
        """
        server = None
        name = args[0]
    else:
        """
        查询 SRV ID
        """
        server = args[0]
        name = args[1]
    server = Server(server, event.group_id).server
    if server is None:
        await serendipity_v2_matcher.finish(PROMPT.ServerNotExist)
    data = await v2_serendipity(server, name, True)
    await serendipity_v2_matcher.finish(data)

serendipity_v3_matcher = on_command("jx3_serendipity_v3", aliases={"奇遇v3", "查询v3"}, force_whitespace=True, priority=5)

@serendipity_v3_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    if argument.extract_plain_text() == "":
        return
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await serendipity_v3_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：查询v3 <服务器> <角色名>")
    if len(args) == 1:
        """
        查询 ID
        """
        server = None
        id = args[0]
    else:
        """
        查询 SRV ID
        """
        server = args[0]
        id = args[1]
    server = Server(server, event.group_id).server
    if server is None:
        await serendipity_v3_matcher.finish(PROMPT.ServerNotExist)
    data = await v3_serendipity(server, id)
    await serendipity_v3_matcher.finish(data)

serendipity_v4_matcher = on_command("jx3_serendipity_v4", aliases={"奇遇v4", "查询v4"}, force_whitespace=True, priority=5)

@serendipity_v4_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    if argument.extract_plain_text() == "":
        return
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await serendipity_v4_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：查询v4 <服务器> <角色名>")
    server, name = (None, args[0]) if len(args) == 1 else (args[0], args[1])
    server = Server(server, event.group_id).server
    if server is None:
        await serendipity_v4_matcher.finish(PROMPT.ServerNotExist)
    data = await v4_serendipity(server, name)
    await serendipity_v4_matcher.finish(data)

pet_serendipity_matcher = on_command("jx3_pet_serendipity", aliases={"宠物奇遇"}, force_whitespace=True, priority=5)

@pet_serendipity_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    """
    获取个人奇遇记录：

    Example：-宠物奇遇 幽月轮 哭包猫@唯我独尊
    """
    if argument.extract_plain_text() == "":
        return
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [1, 2]:
        await pet_serendipity_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：宠物奇遇 <服务器> <角色名>")
    if len(args) == 1:
        """
        查询 ID
        """
        server = None
        name = args[0]
    else:
        """
        查询 SRV ID
        """
        server = args[0]
        name = args[1]
    server = Server(server, event.group_id).server
    if server is None:
        await pet_serendipity_matcher.finish(PROMPT.ServerNotExist)
    data = await v2_serendipity(server, name, False)
    await pet_serendipity_matcher.finish(data)

preposition_matcher = on_command("jx3_preposition", aliases={"前置", "攻略"}, force_whitespace=True, priority=5)

@preposition_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    serendipity = args.extract_plain_text()
    data = await get_preposition(serendipity)
    if not data:
        await preposition_matcher.finish("唔……没有找到相关信息~")
    else:
        await preposition_matcher.finish(data)
    
submit_serendipity_matcher = on_command("jx3_submit_serendipity_time", aliases={"奇遇时间"}, force_whitespace=True, priority=5)

@submit_serendipity_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    if argument.extract_plain_text() == "":
        return
    args = argument.extract_plain_text().split(" ")
    if len(args) not in [3, 4]:
        await submit_serendipity_matcher.finish(
            "唔……奇遇时间提交命令格式错误！\n" + \
            "示例：奇遇时间 服务器 示例角色 侠行囧途 202402281538\n" + \
            "当群聊绑定服务器后，服务器可以不填写，时间请按照“YYYYmmddHHMMSS”格式填写。"
        )
    if len(args) == 3:
        """
        奇遇时间 ID SNAME STIME
        """
        role = args[0]
        name = args[1]
        time = args[2]
        server = Server(None, event.group_id).server
    else:
        """
        奇遇时间 SRV ID SNAME STIME
        """
        server = Server(args[0], event.group_id).server
        role = args[1]
        name = args[2]
        time = args[3]
    lawful_data: SerendipityData | None | Any = serendipity_db.where_one(SerendipityData(), "server = ? AND roleName = ? AND time = ? AND serendipityName = ?", server, role, 0, name, default=None)
    if lawful_data is None:
        await submit_serendipity_matcher.finish(
            "唔……无法保存时间，可能是以下原因\n" + \
            "1. 该奇遇在数据库中已记录时间；\n" + \
            "2. 给出的奇遇名称不正确；\n" + \
            "3. 角色名称不正确或者存在改名；\n" + \
            "4. 从未使用这里的查询命令。\n" + \
            "请核对上面的问题，然后再试一次。" 
        )
    try:
        lawful_data.time = int(datetime.strptime(time, "%Y%m%d%H%M%S").timestamp())
    except ValueError: # 瞎几把给时间的话...
        await submit_serendipity_matcher.finish("唔……无法识别这个时间，请参考“YYYYmmddHHMMSS”格式，随后再试一次。")
    serendipity_db.save(lawful_data)
    await submit_serendipity_matcher.finish("已将您的奇遇时间记录完毕！")
