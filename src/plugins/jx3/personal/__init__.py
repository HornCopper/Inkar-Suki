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
    
def parse_role_names(input_str: str) -> list[str]:
    extracted_items = re.findall(r"\[(.*?)\]", input_str)
    cleaned_str = re.sub(r"\[.*?\]", '', input_str)
    result = re.split(r'[，、,。/.\\]', cleaned_str)
    result = [item.strip() for item in result if item.strip()]
    return extracted_items + result

personal_bind_matcher = on_command("绑定角色", priority=5, force_whitespace=True)

@personal_bind_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    args = argument.extract_plain_text().strip()
    if args == "":
        return
    args = args.split(" ")
    if len(args) not in [1, 2]:
        await personal_bind_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：绑定角色 <服务器> <角色名>\n参考格式：绑定角色 <服务器> <ID串>\n参考格式：绑定角色 <ID串>")
    if len(args) == 1:
        roles: list[str] = parse_role_names(args[0])
        server = Server(None, event.group_id).server
        if server is None:
            await personal_bind_matcher.finish(PROMPT.ServerNotExist)
    elif len(args) == 2:
        server = args[0]
        roles: list[str] = parse_role_names(args[1])
        server = Server(server, event.group_id).server
        if server is None:
            await personal_bind_matcher.finish(PROMPT.ServerNotExist)
    parsed_roles = [parse_role_name(name, server) for name in roles]
    msg = RoleBind(event.user_id, parsed_roles).bind()
    await personal_bind_matcher.finish(msg)

personal_unbind_matcher = on_command("解绑角色", priority=5, force_whitespace=True)

@personal_unbind_matcher.handle()
async def _(event: GroupMessageEvent, argument: Message = CommandArg()):
    arg = argument.extract_plain_text().strip()
    if arg == "":
        return
    all = False
    if arg == "全部":
        parsed_roles = []
        all = True
        msg = RoleBind(event.user_id, parsed_roles).unbind(all=all)
        await personal_bind_matcher.finish(msg)
    else:
        args = arg.split(" ")
        if len(args) == 1:
            roles: list[str] = parse_role_names(args[0])
            server = Server(None, event.group_id).server
            if server is None:
                await personal_bind_matcher.finish(PROMPT.ServerNotExist)
        elif len(args) == 2:
            server = args[0]
            roles: list[str] = parse_role_names(args[1])
            server = Server(server, event.group_id).server
            if server is None:
                await personal_bind_matcher.finish(PROMPT.ServerNotExist)
        parsed_roles = [parse_role_name(name, server) for name in roles]
        msg = RoleBind(event.user_id, parsed_roles).unbind(all=all)
        await personal_bind_matcher.finish(msg)

all_personal_roles_matcher = on_command("角色列表", priority=5, force_whitespace=True)

@all_personal_roles_matcher.handle()
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
    await all_personal_roles_matcher.finish(ms.at(event.user_id) + f" {msg}")