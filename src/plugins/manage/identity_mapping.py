from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from src.utils.command import on_command
from src.utils.database.identity import ID_HELP, MATCH_PERMISSION, match_identity
from src.utils.identity import IdentityScope
from src.utils.permission import check_permission, denied

group_matcher = on_command("匹配群", force_whitespace = True, priority = 5)
personal_matcher = on_command("匹配个人", force_whitespace = True, priority = 5)


async def handle_match_identity(matcher: type[Matcher], scope: IdentityScope, event: MessageEvent, args: Message) -> None:
    label = "群" if scope == "group" else "个人"
    help_text = f"格式：匹配{label} -内部ID {'群号' if scope == 'group' else 'QQ号'}"
    if not check_permission(event.user_id, MATCH_PERMISSION):
        await matcher.finish(denied(MATCH_PERMISSION))
        return
    parts = args.extract_plain_text().split()
    if len(parts) != 2:
        await matcher.finish(help_text)
        return
    try:
        # 同步执行，使合并完成前不会在事件循环中插入另一条使用旧身份的命令。
        # 类型由命令决定；服务层沿用带类型的标识，用户仅输入数字。
        prefix = "g" if scope == "group" else "u"
        result = match_identity(prefix + parts[0], prefix + parts[1], event.user_id)
    except ValueError as error:
        await matcher.finish(help_text if str(error) == ID_HELP else str(error))
        return
    if result.already_matched:
        response = f"已存在{label}匹配：{result.source_id} → {result.target_id}，没有重复合并。"
    else:
        response = (
            f"{label}匹配成功：{result.source_id} → {result.target_id}\n"
            f"已归并数据（处理 {result.changed_rows} 条记录），后续两种 ID 使用同一份数据。\n"
            "列表去重合并；冲突配置保留有效数据较多的一侧，同分保留号码侧；金币和签到次数取较大值。"
        )
    await matcher.finish(response)


@group_matcher.handle()
async def handle_group_match(event: MessageEvent, args: Message = CommandArg()) -> None:
    await handle_match_identity(group_matcher, "group", event, args)


@personal_matcher.handle()
async def handle_personal_match(event: MessageEvent, args: Message = CommandArg()) -> None:
    await handle_match_identity(personal_matcher, "user", event, args)
