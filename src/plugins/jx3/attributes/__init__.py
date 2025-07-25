from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Message,
    GroupMessageEvent
)
from nonebot.params import CommandArg

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from utils.database.attributes import parse_conditions
from src.plugins.preferences.app import Preference

from .v2 import get_attr_v2
from .v2_remake import get_attr_v2_remake
from .v4 import get_attr_v4

attribute_matcher = on_command("jx3_attribute", aliases={"属性", "查装"}, force_whitespace=True, priority=5)

@attribute_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) not in [1, 2, 3]:
        await attribute_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：属性 <服务器> <角色名>\n参考格式：属性 [角色名·服务器]\n参加格式：属性 角色名·服务器")
    if len(arg) == 1:
        server = None
        role_name = arg[0]
        tags = ""
    elif len(arg) == 2:
        if parse_conditions(arg[-1]):
            server = None
            role_name = arg[0]
            tags = arg[1]
        else:
            server = arg[0]
            role_name = arg[1]
            tags = ""
    elif len(arg) == 3:
        server = arg[0]
        role_name = arg[1]
        tags = arg[-1]
    server = Server(server, event.group_id).server
    if not server:
        await attribute_matcher.finish(PROMPT.ServerNotExist)
    ver = Preference(event.user_id, "", "").setting("属性")
    if ver == "v2":
        data = await get_attr_v2(server, role_name)
    elif ver == "v2r":
        data = await get_attr_v2_remake(server, role_name, segment=True)
    elif ver == "v4":
        data = await get_attr_v4(server, role_name, tags)
    await attribute_matcher.finish(data)

attribute_v2_matcher = on_command("jx3_addritube_v2", aliases={"属性v2", "查装v2"}, force_whitespace=True, priority=5)

@attribute_v2_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """
    查询某玩家的装备：

    Example：-属性 幽月轮 哭包猫@唯我独尊
    Example：-查装 幽月轮 哭包猫@唯我独尊
    """
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) not in [1, 2]:
        await attribute_v2_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：属性v2 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        role = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        role = arg[1]
    server = Server(server, event.group_id).server
    if not server:
        await attribute_v2_matcher.finish(PROMPT.ServerNotExist)
    data = await get_attr_v2(server, role)
    await attribute_v2_matcher.finish(data)

attribute_v2remake_matcher = on_command("jx3_addritube_v2_remake", aliases={"属性v2r", "查装v2r"}, force_whitespace=True, priority=5)

@attribute_v2remake_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) not in [1, 2]:
        await attribute_v2remake_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：属性v2r <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        role = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        role = arg[1]
    server = Server(server, event.group_id).server
    if not server:
        await attribute_v2remake_matcher.finish(PROMPT.ServerNotExist)
    data = await get_attr_v2_remake(server, role, segment=True)
    await attribute_v2remake_matcher.finish(data)

attribute_v4_matcher = on_command("jx3_addritube_v4", aliases={"属性v4", "查装v4"}, force_whitespace=True, priority=5)

@attribute_v4_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().strip().split(" ")
    if len(arg) not in [1, 2, 3]:
        await attribute_v4_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：属性v4 <服务器> <角色名>")
    if len(arg) == 1:
        server = None
        role_name = arg[0]
        tags = ""
    elif len(arg) == 2:
        if parse_conditions(arg[-1]):
            server = None
            role_name = arg[0]
            tags = arg[1]
        else:
            server = arg[0]
            role_name = arg[1]
            tags = ""
    elif len(arg) == 3:
        server = arg[0]
        role_name = arg[1]
        tags = arg[-1]
    server = Server(server, event.group_id).server
    if not server:
        await attribute_v4_matcher.finish(PROMPT.ServerNotExist)
    data = await get_attr_v4(server, role_name, tags)
    await attribute_v4_matcher.finish(data)