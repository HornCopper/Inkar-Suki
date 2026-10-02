import asyncio
from typing import Literal

from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.params import CommandArg

from src.config import Config
from src.utils.command import on_command
from src.utils.permission import get_permission_holders


PAGE_SIZE = 20
HELP = """格式：权限反查 <用户|群> <权限节点> [页码]
例如：权限反查 群 group.application.chat_records
例如：权限反查 用户 economy.checkin.pool.manage
按实际生效的权限匹配，包含父节点授权和通配符授权，排除被显式拒绝的对象。
用户范围包含 Bot 主人；群范围查询已保存群配置。每页 20 个。"""

PermissionHoldersMatcher = on_command(
    "permissionholders", aliases={"权限反查"}, force_whitespace=True, priority=5,
)


@PermissionHoldersMatcher.handle()
async def handle_permission_holders(event: MessageEvent, args: Message = CommandArg()) -> None:
    if str(event.user_id) not in Config.bot_basic.bot_owner:
        await PermissionHoldersMatcher.finish("只有 Bot 主人可以按权限节点查询用户或群。")
        return
    parts = args.extract_plain_text().split()
    if len(parts) not in {2, 3} or parts[0] not in {"用户", "user", "u", "群", "group", "g"}:
        await PermissionHoldersMatcher.finish(HELP)
        return
    scope: Literal["user", "group"] = "user" if parts[0] in {"用户", "user", "u"} else "group"
    label = "用户" if scope == "user" else "群"
    node = parts[1].strip(".")
    try:
        try:
            page = int(parts[2]) if len(parts) == 3 else 1
        except ValueError:
            raise ValueError("页码需要是正整数。") from None
        if page < 1:
            raise ValueError("页码需要是正整数。")
        holders = await asyncio.to_thread(get_permission_holders, node, scope)
        pages = max(1, (len(holders) + PAGE_SIZE - 1) // PAGE_SIZE)
        if page > pages:
            raise ValueError(f"页码超出范围，共 {pages} 页。")
        offset = (page - 1) * PAGE_SIZE
        lines = [f"权限反查 · {label}\n节点：{node}\n共 {len(holders)} 个{label} · 第 {page}/{pages} 页"]
        lines.extend(f"{index}. {target_id}" for index, target_id in enumerate(holders[offset:offset + PAGE_SIZE], start=offset + 1))
        if not holders:
            lines.append(f"没有具有该权限节点的{label}。")
        if page < pages:
            lines.append(f"下一页：权限反查 {label} {node} {page + 1}")
        response = "\n".join(lines)
    except ValueError as error:
        response = str(error)
    await PermissionHoldersMatcher.finish(response)
