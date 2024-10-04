from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.params import CommandArg

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.database.operation import set_group_settings
from src.utils.database.player import get_uid_data
from src.utils.permission import check_permission

def bind_srv(group_id: str, server: str | None):
    if server != "":
        server_ = Server(server).server
        if not server_:
            return [PROMPT.ServerNotExist]
        else:
            set_group_settings(group_id, "server", server_)
    else:
        set_group_settings(group_id, "server", "")

BindServerMatcher = on_command("jx3_bind", aliases={"绑定", "绑定区服"}, force_whitespace=True, priority=5)

@BindServerMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    personal_data = await bot.call_api("get_group_member_info", group_id = event.group_id, user_id = event.user_id, no_cache = True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    robot_admin = check_permission(str(event.user_id), 5)
    if not group_admin and not robot_admin:
        await BindServerMatcher.finish("唔……只有群主或管理员才可以修改哦！")
    server = args.extract_plain_text()
    group_id = str(event.group_id)
    exact_server = Server(server).server
    bind_srv(group_id=group_id, server=exact_server if server else "")
    if server == "":
        await BindServerMatcher.finish("已清除本群的绑定信息！")
    if server is None:
        await BindServerMatcher.finish("您给出的服务器名称音卡似乎没有办法理解，尝试使用一个更通俗的名称或者官方标准名称？")
    if not isinstance(exact_server, str):
        return
    await BindServerMatcher.finish("绑定成功！\n当前区服为：" + exact_server)

RoleCheckMatcher = on_command("jx3_checkrole", aliases={"提交角色"}, priority=5, force_whitespace=True)

@RoleCheckMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await RoleCheckMatcher.finish("唔……命令错误，请检查后重试！\n命令格式：提交角色 服务器 UID")
    if len(arg) == 1:
        server = None
        uid = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        uid = arg[1]
    serverInstance = Server(server, event.group_id)
    if not serverInstance.server:
        await RoleCheckMatcher.finish(PROMPT.ServerNotExist)
    msg = await get_uid_data(uid, serverInstance.server)
    if not isinstance(msg, str):
        return
    await RoleCheckMatcher.finish(msg)