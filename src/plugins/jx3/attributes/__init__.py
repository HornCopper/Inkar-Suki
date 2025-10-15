import asyncio
from concurrent.futures import ThreadPoolExecutor
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    GroupMessageEvent,
    GroupUploadNoticeEvent
)
from nonebot.params import CommandArg

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.database.attributes import JX3PlayerAttribute, parse_conditions
from src.plugins.preferences.app import Preference
from src.plugins.notice import notice
from src.utils.network import Request
from src.utils.analyze import check_number
from src.utils.database.operation import get_group_settings

from .v2_remake import get_attr_v2_remake, get_attr_v2_remake_build, get_attr_v2_remake_global
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
    if ver == "v2r":
        data = await get_attr_v2_remake(server, role_name, segment=True)
    elif ver == "v4":
        data = await get_attr_v4(server, role_name, tags)
    await attribute_matcher.finish(data)

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

attribute_repo = on_command("jx3_attribute_repo", aliases={"属性库"}, priority=5, force_whitespace=True)

@attribute_repo.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip() == "":
        return
    num = args.extract_plain_text().strip()
    if not check_number(num):
        await attribute_repo.finish("属性库仅支持使用全服ID进行查看！")
    image = await get_attr_v2_remake_global(int(num))
    await attribute_repo.finish(image)

attribute_build = on_command("jx3_attribute_build", aliases={"配装器"}, priority=5, force_whitespace=True)

@attribute_build.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text().strip() == "":
        return
    jcl_line = args.extract_plain_text().strip()
    image = await get_attr_v2_remake_build(jcl_line)
    await attribute_build.finish(image)

attribute_db_executor = ThreadPoolExecutor(max_workers=1)

@notice.handle()
async def _(bot: Bot, event: GroupUploadNoticeEvent):
    if event.file.name.endswith(".jcl"):
        if event.file.name[:3] in ["CQC", "IKS"]:
            return
        msg = "以下全局玩家ID完成入库："
        response = await Request(event.model_dump()["file"]["url"]).get()
        response.encoding = "gbk"
        jcl_text = response.text
        if len(response.content) > 2 * 1024 * 1024 and "Preview" not in get_group_settings(event.group_id, "additions"):
            return
        attributes_data = await JX3PlayerAttribute.from_jcl(jcl_text)
        loop = asyncio.get_running_loop()
        await asyncio.gather(*[
            loop.run_in_executor(attribute_db_executor, each_data.save)
            for each_data in attributes_data
        ])
        for each_data in attributes_data:
            msg += f"\n{each_data.name}（{each_data.global_role_id}）"
        await bot.send_group_msg(group_id=event.group_id, message=msg)