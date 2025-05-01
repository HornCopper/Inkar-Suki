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
    elif len(args) == 2:
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
    elif ver == "v3":
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
    elif len(args) == 2:
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
    elif len(args) == 2:
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
    elif len(args) == 2:
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
    if len(args) == 4:
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