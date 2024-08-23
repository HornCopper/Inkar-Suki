from typing import Optional

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.params import CommandArg

from src.tools.basic.prompts import PROMPT
from src.tools.basic.server import server_mapping
from src.tools.basic.group import setGroupSettings
from src.tools.permission import checker

from .role import *

def bind_srv(group_id: str, server: Optional[str]):
    if not server == "":
        # 当server为空表示要清空
        server_ = server_mapping(server)
        if not server_:
            return [PROMPT.ServerNotExist]
    setGroupSettings(group_id, "server", server_)

server_bind = on_command("jx3_bind", aliases={"绑定", "绑定区服"}, force_whitespace=True, priority=5)

@server_bind.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    personal_data = await bot.call_api("get_group_member_info", group_id = event.group_id, user_id = event.user_id, no_cache = True)
    group_admin = personal_data["role"] in ["owner", "admin"]
    robot_admin = checker(str(event.user_id), 5)
    if not group_admin and not robot_admin:
        await server_bind.finish("唔……只有群主或管理员才可以修改哦！")
    server = args.extract_plain_text()
    group_id = str(event.group_id)
    exact_server = server_mapping(server)
    bind_srv(group_id=group_id, server=exact_server if server else "")
    if server == "":
        await server_bind.finish("已清除本群的绑定信息！")
    if server == None:
        await server_bind.finish("您给出的服务器名称音卡似乎没有办法理解，尝试使用一个更通俗的名称或者官方标准名称？")
    if not isinstance(exact_server, str):
        return
    await server_bind.finish("绑定成功！\n当前区服为：" + exact_server)


check_role = on_command("jx3_checkrole", aliases={"提交角色"}, priority=5, force_whitespace=True)

@check_role.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    arg = args.extract_plain_text().split(" ")
    if len(arg) not in [1, 2]:
        await check_role.finish("唔……命令错误，请检查后重试！\n命令格式：提交角色 服务器 UID")
    if len(arg) == 1:
        server = None
        id = arg[0]
    elif len(arg) == 2:
        server = arg[0]
        id = arg[1]
    msg = await getRoleData(id, server, group_id=str(event.group_id))
    if not isinstance(msg, str):
        return
    await check_role.finish(msg)