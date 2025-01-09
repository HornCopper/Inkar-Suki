from typing import Any

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment as ms

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.utils.database import db
from src.utils.database.classes import PersonalSettings

import re

from .bind import RoleBind

def parse_role_name(role_name: str, group_server: str) -> tuple[str, str]:
    if "·" in role_name:
        role_name, role_server = role_name.split("·", 1)
        return role_name, role_server
    else:
        return role_name, group_server

PersonalBindMathcer = on_command("绑定角色", priority=5, force_whitespace=True)

@PersonalBindMathcer.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().strip()
    roles: list[str] = re.findall(r"\[(.*?)\]", arg) if "、" not in arg else arg.split("、")
    server = Server(None, event.group_id).server
    if server is None:
        await PersonalBindMathcer.finish(PROMPT.ServerNotExist)
    parsed_roles = [parse_role_name(name, server) for name in roles]
    msg = RoleBind(event.user_id, parsed_roles).bind()
    await PersonalBindMathcer.finish(msg)

PersonalUnbindMathcer = on_command("解绑角色", priority=5, force_whitespace=True)

@PersonalUnbindMathcer.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().strip()
    all = False
    if arg == "全部":
        parsed_roles = []
        all = True
    else:
        roles: list[str] = re.findall(r"\[(.*?)\]", arg)
        server = Server(None, event.group_id).server
        if server is None:
            await PersonalUnbindMathcer.finish(PROMPT.ServerNotExist)
        parsed_roles = [parse_role_name(name, server) for name in roles]
    msg = RoleBind(event.user_id, parsed_roles).unbind(all=all)
    await PersonalUnbindMathcer.finish(msg)

AllBoundRolesMatcher = on_command("角色列表", priority=5, force_whitespace=True)

@AllBoundRolesMatcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if args.extract_plain_text() != "":
        return
    personal_settings: PersonalSettings | Any = db.where_one(PersonalSettings(), "user_id = ?", str(event.user_id), default=PersonalSettings())
    roles = personal_settings.roles
    if not roles:
        msg = "您尚未绑定任何角色！"
    else:
        msg = "您当前绑定了如下角色：\n" + "\n".join(
            [
                f"{r.roleName}·{r.serverName}"
                for r
                in roles
            ]
        )
    await AllBoundRolesMatcher.finish(ms.at(event.user_id) + f" {msg}")