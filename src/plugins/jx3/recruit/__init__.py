from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment as ms

from src.tools.basic.server import getGroupServer, server_mapping
from src.tools.basic.group import getGroupSettings
from src.tools.utils.file import get_content_local
from src.tools.config import Config

from .api import *

recruit_v2_ = on_command("jx3_recruit", aliases={"招募"}, force_whitespace=True, priority=5)


@recruit_v2_.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if not Config.jx3.api.enable:
        return
    filter = False
    addtions = getGroupSettings(str(event.group_id), "addtions")
    if not isinstance(addtions, list):
        return
    if "招募过滤" in addtions:
        filter = True
    arg = args.extract_plain_text()
    if arg == "":
        group_server = getGroupServer(str(event.group_id))
        if not group_server:
            await recruit_v2_.finish("尚未绑定服务器，请携带服务器参数使用！")
        data = await recruit_v2(group_server, filter=filter)
    else:
        arg = arg.split(" ")
        if len(arg) not in [1, 2]:
            await recruit_v2_.finish("参数不正确哦，只能有1或2个参数~")
        server = server_mapping(arg[0], str(event.group_id))
        if len(arg) == 1:
            copy = arg[0] if not server_mapping(arg[0]) else ""  # 当第一个参数是服务器的话则为空
        else:
            copy = arg[1]
        data = await recruit_v2(server, copy, False, filter)
    if isinstance(data, list):
        await recruit_v2_.finish(data[0])
    elif isinstance(data, str):
        data = get_content_local(data)
        await recruit_v2_.finish(ms.image(data))


jx3_cmd_recruit_local = on_command("jx3_recruit_local", aliases={"本服招募"}, force_whitespace=True, priority=5)


@jx3_cmd_recruit_local.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if not Config.jx3.api.enable:
        return
    arg = args.extract_plain_text()
    filter = False
    addtions = getGroupSettings(str(event.group_id), "addtions")
    if not isinstance(addtions, list):
        return
    if "招募过滤" in addtions:
        filter = True
    if arg == "":
        group_server = getGroupServer(str(event.group_id))
        if not group_server:
            await jx3_cmd_recruit_local.finish("尚未绑定服务器，请携带服务器参数使用！")
        data = await recruit_v2(group_server, local=True, filter=filter)
    else:
        arg = arg.split(" ")
        if len(arg) not in [1, 2]:
            await jx3_cmd_recruit_local.finish("参数不正确哦，只能有1或2个参数~")
        server = server_mapping(arg[0], str(event.group_id))
        if len(arg) == 1:
            copy = arg[0] if not server_mapping(arg[0]) else ""  # 当第一个参数是服务器的话则为空
        else:
            copy = arg[1]
        data = await recruit_v2(server, copy, True, filter)
    if isinstance(data, list):
        await jx3_cmd_recruit_local.finish(data[0])
    elif isinstance(data, str):
        data = get_content_local(data)
        await jx3_cmd_recruit_local.finish(ms.image(data))