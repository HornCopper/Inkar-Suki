from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, PrivateMessageEvent
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import CommandArg

from .app import (
    bind_team_member,
    consume_bind_kungfu_selection,
    consume_delete_team_confirmation,
    create_team,
    delete_member,
    delete_team,
    format_bind_kungfu_selection,
    list_owned_teams,
    prepare_bind_team_member_selection,
    prepare_delete_team_confirmation,
    query_team_status,
    render_team_health_check,
    remember_bind_kungfu_selection,
    reset_feature_code,
    team_management_help,
)


TeamHealthMessageEvent = GroupMessageEvent | PrivateMessageEvent


def _group_id(event: TeamHealthMessageEvent) -> int | None:
    return event.group_id if isinstance(event, GroupMessageEvent) else None


register_raid_team_matcher = on_command("注册团队", priority=5, force_whitespace=True)


@register_raid_team_matcher.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    team_name = args.extract_plain_text().strip()
    if team_name == "":
        await register_raid_team_matcher.finish("参考格式：注册团队 <团队名>")
    await register_raid_team_matcher.finish(
        create_team(event.group_id, event.user_id, team_name)
    )


bind_raid_team_matcher = on_command("绑定团队", priority=5, force_whitespace=True)
select_bind_kungfu_matcher = on_message(priority=10, block=False)


@bind_raid_team_matcher.handle()
async def _(event: TeamHealthMessageEvent, args: Message = CommandArg()):
    parts = args.extract_plain_text().strip().split()
    if len(parts) not in [3, 4]:
        await bind_raid_team_matcher.finish(
            "参考格式：绑定团队 <区服> <角色> <团队唯一特征码>\n"
            "多心法角色：绑定团队 <区服> <角色> <心法> <团队唯一特征码>"
        )
    if len(parts) == 3:
        server, role, feature_code = parts
        kungfu = None
        try:
            selection = await prepare_bind_team_member_selection(
                _group_id(event),
                event.user_id,
                server,
                role,
                feature_code,
            )
        except Exception as exc:
            logger.exception(f"绑定团队失败：{exc}")
            await bind_raid_team_matcher.finish(f"绑定失败：{exc}")
        if isinstance(selection, str):
            await bind_raid_team_matcher.finish(selection)
        if isinstance(selection, dict):
            remember_bind_kungfu_selection(_group_id(event), event.user_id, selection)
            await bind_raid_team_matcher.finish(format_bind_kungfu_selection(selection["options"]))
    else:
        server, role, kungfu, feature_code = parts
    try:
        msg = await bind_team_member(
            _group_id(event),
            event.user_id,
            server,
            role,
            feature_code,
            kungfu,
        )
    except Exception as exc:
        logger.exception(f"绑定团队失败：{exc}")
        msg = f"绑定失败：{exc}"
    await bind_raid_team_matcher.finish(msg)


@select_bind_kungfu_matcher.handle()
async def _(event: TeamHealthMessageEvent):
    text = event.message.extract_plain_text().strip()
    if not text.isdigit() and text not in {"取消", "算了"}:
        return
    try:
        msg = await consume_bind_kungfu_selection(
            _group_id(event),
            event.user_id,
            text,
        )
    except Exception as exc:
        logger.exception(f"绑定团队失败：{exc}")
        msg = f"绑定失败：{exc}"
    if msg is None:
        return
    await select_bind_kungfu_matcher.finish(msg)


raid_team_manage_matcher = on_command("团队管理", priority=5, force_whitespace=True)
confirm_delete_team_matcher = on_command("确认删除", priority=5, force_whitespace=True)


@raid_team_manage_matcher.handle()
async def _(event: TeamHealthMessageEvent, args: Message = CommandArg()):
    parts = args.extract_plain_text().strip().split()
    if not parts:
        await raid_team_manage_matcher.finish(team_management_help())
    if len(parts) == 1:
        if parts[0] in {"help", "帮助", "指令", "菜单"}:
            await raid_team_manage_matcher.finish(team_management_help())
        if parts[0] == "我的团队":
            await raid_team_manage_matcher.finish(list_owned_teams(event.user_id))
        await raid_team_manage_matcher.finish(team_management_help())

    team_name = parts[0]
    action = parts[1]

    if action in {"help", "帮助", "指令", "菜单"}:
        await raid_team_manage_matcher.finish(team_management_help())

    if action == "重置特征码":
        if len(parts) != 2:
            await raid_team_manage_matcher.finish("参考格式：团队管理 <团队名> 重置特征码")
        await raid_team_manage_matcher.finish(reset_feature_code(event.user_id, team_name))

    if action in {"状态", "查询", "查询状态"}:
        if len(parts) != 2:
            await raid_team_manage_matcher.finish("参考格式：团队管理 <团队名> 状态")
        await raid_team_manage_matcher.finish(query_team_status(event.user_id, team_name))

    if action == "删除团队":
        if len(parts) == 3 and parts[2] in {"确认", "确认删除"}:
            await raid_team_manage_matcher.finish(delete_team(event.user_id, team_name))
        if len(parts) != 2:
            await raid_team_manage_matcher.finish(
                "参考格式：团队管理 <团队名> 删除团队\n"
                "直接确认：团队管理 <团队名> 删除团队 确认"
            )
        await raid_team_manage_matcher.finish(
            prepare_delete_team_confirmation(event.user_id, team_name)
        )

    if action == "删除成员":
        if len(parts) == 3:
            await raid_team_manage_matcher.finish(
                delete_member(event.user_id, team_name, parts[2], group_id=_group_id(event))
            )
        if len(parts) == 4:
            await raid_team_manage_matcher.finish(
                delete_member(event.user_id, team_name, parts[3], parts[2], _group_id(event))
            )
        await raid_team_manage_matcher.finish(
            "参考格式：团队管理 <团队名> 删除成员 <角色名>\n"
            "同名跨区服：团队管理 <团队名> 删除成员 <区服> <角色名>"
        )

    if action == "体检":
        if len(parts) != 2:
            await raid_team_manage_matcher.finish("参考格式：团队管理 <团队名> 体检")
        await raid_team_manage_matcher.send("团队体检中，请稍等片刻。")
        result = await render_team_health_check(event.user_id, team_name)
        try:
            await raid_team_manage_matcher.finish(result)
        except ActionFailed:
            await raid_team_manage_matcher.finish(
                "团队体检图片已生成，但 QQ/NapCat 拒绝了图片上传，建议重启 NapCat 后重试。"
            )

    await raid_team_manage_matcher.finish(
        "未知团队管理动作。\n" + team_management_help()
    )


@confirm_delete_team_matcher.handle()
async def _(event: TeamHealthMessageEvent, args: Message = CommandArg()):
    team_name = args.extract_plain_text().strip()
    if not team_name:
        await confirm_delete_team_matcher.finish("参考格式：确认删除 <团队名>")
    error = consume_delete_team_confirmation(event.user_id, team_name)
    if error is not None:
        await confirm_delete_team_matcher.finish(error)
    await confirm_delete_team_matcher.finish(delete_team(event.user_id, team_name))
