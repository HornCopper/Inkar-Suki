from __future__ import annotations

import asyncio
import hashlib
import html
import json
import secrets
from pathlib import Path
from typing import Any, cast

from jinja2 import Template
from nonebot.adapters.onebot.v11 import MessageSegment as ms
from nonebot.log import logger

from src.const.jx3.kungfu import Kungfu
from src.const.jx3.server import Server
from src.const.path import ASSETS, TEMPLATES, build_path
from src.const.prompts import PROMPT
from src.utils.analyze import check_number
from src.utils.database import db
from src.utils.database.attributes import JX3PlayerAttribute
from src.utils.database.classes import RaidTeamHealth, RoleData
from src.utils.database.player import get_uid_data, search_player
from src.utils.file import read
from src.utils.generate import generate
from src.utils.time import Time

from src.plugins.jx3.calculator.base import normalize_calculator_jcl_data
from src.plugins.jx3.calculator.equipment_rating import (
    RANK_THEMES,
    _equipment_rating_pve_tag,
    _grade_icon,
    _prepare_adaptive_consumables,
    _prepare_tank_vitality_conversion,
    _rating_pve_kungfu_options,
    _request_equipment_rating_data,
    record_equipment_rating_rank,
)


TEAM_HEALTH_CAPACITY = 25
TEAM_HEALTH_TEMPLATE = build_path(TEMPLATES, ["jx3", "team_health_check.html"])
TEAM_HEALTH_CACHE_VERSION = 2
TEAM_HEALTH_CANDIDATE_LEVEL = {
    "min": 32500,
    "max": 43000,
}
DELETE_TEAM_CONFIRM_TTL = 300
BIND_KUNGFU_SELECT_TTL = 300
_PENDING_DELETE_TEAMS: dict[tuple[int, str], int] = {}
_PENDING_BIND_KUNGFU_SELECTIONS: dict[tuple[int | None, int], dict[str, Any]] = {}


def _escape(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _normalize_team_name(team_name: str) -> str:
    return team_name.strip()


def _delete_team_confirm_key(user_id: int, team_name: str) -> tuple[int, str]:
    return int(user_id), _normalize_team_name(team_name)


def _bind_kungfu_selection_key(group_id: int | None, user_id: int) -> tuple[int | None, int]:
    return (int(group_id) if group_id is not None else None), int(user_id)


def _cleanup_delete_team_confirmations() -> None:
    now = Time().raw_time
    expired_keys = [
        key
        for key, timestamp in _PENDING_DELETE_TEAMS.items()
        if now - int(timestamp) > DELETE_TEAM_CONFIRM_TTL
    ]
    for key in expired_keys:
        _PENDING_DELETE_TEAMS.pop(key, None)


def _cleanup_bind_kungfu_selections() -> None:
    now = Time().raw_time
    expired_keys = [
        key
        for key, context in _PENDING_BIND_KUNGFU_SELECTIONS.items()
        if now - int(context.get("timestamp") or 0) > BIND_KUNGFU_SELECT_TTL
    ]
    for key in expired_keys:
        _PENDING_BIND_KUNGFU_SELECTIONS.pop(key, None)


def _format_time(timestamp: Any) -> str:
    try:
        return Time(int(timestamp)).format("%Y-%m-%d %H:%M")
    except Exception:
        return "-"


def _owned_team(creator_id: int, team_name: str) -> RaidTeamHealth | None:
    return cast(RaidTeamHealth | None, db.where_one(
        RaidTeamHealth(),
        "creator_id = ? AND team_name = ?",
        int(creator_id),
        team_name,
        default=None,
    ))


def _owned_teams(creator_id: int) -> list[RaidTeamHealth]:
    teams = cast(list[RaidTeamHealth], db.where_all(
        RaidTeamHealth(),
        "creator_id = ?",
        int(creator_id),
        default=[],
    ))
    return sorted(
        list(teams or []),
        key=lambda team: (int(team.create_time or 0), str(team.team_name or "")),
    )


def _team_by_feature_code(feature_code: str) -> RaidTeamHealth | None:
    return cast(RaidTeamHealth | None, db.where_one(
        RaidTeamHealth(),
        "feature_code = ?",
        feature_code.strip().upper(),
        default=None,
    ))


def _generate_feature_code() -> str:
    while True:
        code = secrets.token_hex(4).upper()
        if _team_by_feature_code(code) is None:
            return code


def _member_key(member: dict[str, Any]) -> tuple[str, str]:
    return (
        str(member.get("server") or ""),
        str(member.get("role_name") or ""),
    )


async def _resolve_player(server: str, role: str) -> RoleData | None:
    try:
        if check_number(role):
            player_data = await search_player(
                role_name=role,
                role_id=role,
                server_name=server,
                local_lookup=True,
            )
            if player_data.roleId == "":
                player_data = await get_uid_data(role_id=role, server=server, msg=False)
        else:
            player_data = await search_player(role_name=role, server_name=server)
    except Exception:
        return None
    if not player_data or player_data.roleId == "" or player_data.globalRoleId == "":
        return None
    return player_data


async def _rating_equip(global_role_id: int, kungfu_id: int) -> JX3PlayerAttribute | None:
    try:
        pve_tag = _equipment_rating_pve_tag(kungfu_id)
        pve_equips = await JX3PlayerAttribute.from_database(global_role_id, pve_tag, all=True)
    except Exception:
        return None
    if not pve_equips:
        return None
    return next(
        (
            equip
            for equip in pve_equips
            if int(equip.kungfu_id) == int(kungfu_id) and equip.tag == "PVE"
        ),
        None,
    )


async def _select_kungfu(global_role_id: int, kungfu_name: str | None) -> int | str:
    try:
        options = await _rating_pve_kungfu_options(global_role_id)
    except Exception as exc:
        return f"绑定失败：读取角色装备数据失败：{exc}"
    if not options:
        return "未找到可用于装备评级的 PVE 装备数据，请先使用「提交属性 <区服> <角色> <心法>」提交茗伊装备导出码。"

    if kungfu_name:
        kungfu_id = Kungfu(kungfu_name).id
        if kungfu_id is None:
            return PROMPT.KungfuNotExist
        if not any(int(option["kungfu_id"]) == int(kungfu_id) for option in options):
            option_names = "、".join(str(option["name"]) for option in options)
            return f"该角色没有 {kungfu_name} 的可评级 PVE 装备数据。当前可选心法：{option_names}"
        return int(kungfu_id)

    if len(options) == 1:
        return int(options[0]["kungfu_id"])

    option_lines = [
        f"{index}. {option['name']}"
        for index, option in enumerate(options, start=1)
    ]
    return (
        "检测到该角色有多个可用于装备评级的 PVE 心法，请指定心法：\n"
        + "\n".join(option_lines)
        + "\n可直接回复序号，或使用：绑定团队 <区服> <角色> <心法> <团队唯一特征码>"
    )


async def _resolve_bind_target(
    group_id: int | None,
    operator_id: int,
    server_arg: str,
    role_arg: str,
    feature_code: str,
) -> str | tuple[RaidTeamHealth, str, RoleData]:
    team = _team_by_feature_code(feature_code)
    if team is None:
        return "绑定失败：团队唯一特征码无效。"
    if group_id is None:
        if int(team.creator_id) != int(operator_id):
            return "绑定失败：私聊绑定仅限团队创建者使用。"
        group_context = int(team.group_id)
    elif int(team.group_id) != int(group_id):
        return "绑定失败：该团队只允许在注册所在群绑定成员。"
    else:
        group_context = int(group_id)

    server = Server(server_arg, group_context).server
    if server is None:
        return PROMPT.ServerNotExist

    player_data = await _resolve_player(server, role_arg)
    if player_data is None:
        return "绑定失败：未找到角色信息，请检查区服和角色名。"
    return team, server, player_data


def format_bind_kungfu_selection(options: list[dict[str, Any]]) -> str:
    option_lines = [
        f"{index}. {option['name']}"
        for index, option in enumerate(options, start=1)
    ]
    return (
        "检测到该角色有多个可用于装备评级的 PVE 心法，请指定心法：\n"
        + "\n".join(option_lines)
        + "\n请直接回复序号；回复 0 或 取消 可取消本次绑定。"
    )


async def prepare_bind_team_member_selection(
    group_id: int | None,
    operator_id: int,
    server_arg: str,
    role_arg: str,
    feature_code: str,
) -> dict[str, Any] | str | None:
    target = await _resolve_bind_target(group_id, operator_id, server_arg, role_arg, feature_code)
    if isinstance(target, str):
        return target
    _, _, player_data = target

    try:
        options = await _rating_pve_kungfu_options(int(player_data.globalRoleId))
    except Exception as exc:
        return f"绑定失败：读取角色装备数据失败：{exc}"
    if not options:
        return "未找到可用于装备评级的 PVE 装备数据，请先使用「提交属性 <区服> <角色> <心法>」提交茗伊装备导出码。"
    if len(options) == 1:
        return None
    return {
        "server": server_arg,
        "role": role_arg,
        "feature_code": feature_code,
        "options": options,
    }


def remember_bind_kungfu_selection(
    group_id: int | None,
    user_id: int,
    selection: dict[str, Any],
) -> None:
    _cleanup_bind_kungfu_selections()
    context = dict(selection)
    context["timestamp"] = Time().raw_time
    _PENDING_BIND_KUNGFU_SELECTIONS[_bind_kungfu_selection_key(group_id, user_id)] = context


async def consume_bind_kungfu_selection(
    group_id: int | None,
    user_id: int,
    text: str,
) -> str | None:
    _cleanup_bind_kungfu_selections()
    key = _bind_kungfu_selection_key(group_id, user_id)
    context = _PENDING_BIND_KUNGFU_SELECTIONS.get(key)
    if context is None:
        return None

    text = text.strip()
    if text in {"0", "取消", "算了"}:
        _PENDING_BIND_KUNGFU_SELECTIONS.pop(key, None)
        return "已取消绑定团队。"
    if not text.isdigit():
        return None

    options = context.get("options")
    index = int(text) - 1
    if not isinstance(options, list) or index < 0 or index >= len(options):
        return "超出可选范围，请重新选择，或回复 0 取消。"

    _PENDING_BIND_KUNGFU_SELECTIONS.pop(key, None)
    kungfu = str(options[index].get("name") or "")
    return await bind_team_member(
        group_id,
        user_id,
        str(context["server"]),
        str(context["role"]),
        str(context["feature_code"]),
        kungfu,
    )


def create_team(group_id: int, creator_id: int, team_name: str) -> str:
    team_name = _normalize_team_name(team_name)
    if not team_name:
        return "参考格式：注册团队 <团队名>"
    if any(part.isspace() for part in team_name):
        return "团队名暂不支持空格，请使用一个连续的团队名。"
    if _owned_team(creator_id, team_name) is not None:
        return "注册失败：你名下已经存在同名团队。"

    now = Time().raw_time
    team = RaidTeamHealth(
        creator_id=int(creator_id),
        group_id=int(group_id),
        team_name=team_name,
        feature_code=_generate_feature_code(),
        members=[],
        create_time=now,
        update_time=now,
    )
    db.save(team)
    return (
        f"注册团队成功：{team_name}\n"
        f"团队唯一特征码：{team.feature_code}\n"
        "成员可在本群使用：绑定团队 <区服> <角色> <团队唯一特征码>\n"
        "团队创建者也可私聊使用绑定团队和团队管理。"
    )


async def bind_team_member(
    group_id: int | None,
    user_id: int,
    server_arg: str,
    role_arg: str,
    feature_code: str,
    kungfu_name: str | None = None,
) -> str:
    target = await _resolve_bind_target(group_id, user_id, server_arg, role_arg, feature_code)
    if isinstance(target, str):
        return target
    team, server, player_data = target

    kungfu_id = await _select_kungfu(int(player_data.globalRoleId), kungfu_name)
    if isinstance(kungfu_id, str):
        return kungfu_id

    target_equip = await _rating_equip(int(player_data.globalRoleId), kungfu_id)
    if target_equip is None:
        kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True).name or str(kungfu_id)
        return (
            f"绑定失败：未找到 {player_data.roleName} 的 {kungfu} PVE 装备数据。\n"
            f"请先使用：提交属性 {server} {player_data.roleName} {kungfu}"
        )

    members: list[dict[str, Any]] = list(team.members or [])
    new_member = {
        "user_id": int(user_id),
        "server": player_data.serverName,
        "role_name": player_data.roleName,
        "role_id": player_data.roleId,
        "global_role_id": int(player_data.globalRoleId),
        "kungfu_id": int(kungfu_id),
        "kungfu_name": Kungfu.with_internel_id(kungfu_id, convert_to_pc=True).name or str(kungfu_id),
        "bind_time": Time().raw_time,
        "equip_time": int(target_equip.timestamp),
    }

    existing_index = next(
        (
            index
            for index, member in enumerate(members)
            if _member_key(member) == _member_key(new_member)
        ),
        None,
    )
    overwritten = existing_index is not None
    if existing_index is not None:
        members[existing_index] = new_member
    else:
        if len(members) >= TEAM_HEALTH_CAPACITY:
            return "绑定失败：该团队已满，最多只能绑定 25 个角色。"
        members.append(new_member)

    team.members = members
    team.update_time = Time().raw_time
    db.save(team)
    action = "已覆盖原记录" if overwritten else "绑定成功"
    return (
        f"{action}：{player_data.roleName}·{player_data.serverName} "
        f"({new_member['kungfu_name']})\n"
        f"团队：{team.team_name}，当前成员 {len(members)}/{TEAM_HEALTH_CAPACITY}"
    )


def reset_feature_code(creator_id: int, team_name: str) -> str:
    team = _owned_team(creator_id, _normalize_team_name(team_name))
    if team is None:
        return "未找到你名下的对应团队。"
    team.feature_code = _generate_feature_code()
    team.update_time = Time().raw_time
    db.save(team)
    return f"已重置团队「{team.team_name}」的唯一特征码：{team.feature_code}"


def query_team_status(creator_id: int, team_name: str) -> str:
    team = _owned_team(creator_id, _normalize_team_name(team_name))
    if team is None:
        return "未找到你名下的对应团队。"

    members: list[dict[str, Any]] = list(team.members or [])
    lines = [
        f"团队状态：{team.team_name}",
        f"注册群：{team.group_id}",
        f"团队唯一特征码：{team.feature_code}",
        f"成员数量：{len(members)}/{TEAM_HEALTH_CAPACITY}",
        f"创建时间：{_format_time(team.create_time)}",
        f"更新时间：{_format_time(team.update_time)}",
    ]
    if not members:
        lines.append("成员列表：暂无")
        return "\n".join(lines)

    lines.append("成员列表：")
    for index, member in enumerate(members, start=1):
        lines.append(
            f"{index}. {member.get('role_name')}·{member.get('server')} "
            f"({member.get('kungfu_name')}) "
            f"ID {member.get('role_id')} "
            f"装备更新 {_format_time(member.get('equip_time'))}"
        )
    return "\n".join(lines)


def team_management_help() -> str:
    return (
        "团队管理指令：\n"
        "注册团队 <团队名>\n"
        "绑定团队 <区服> <角色> <团队唯一特征码>\n"
        "绑定团队 <区服> <角色> <心法> <团队唯一特征码>\n"
        "团队管理 我的团队\n"
        "团队管理 <团队名> 状态\n"
        "团队管理 <团队名> 体检\n"
        "团队管理 <团队名> 删除成员 <角色名>\n"
        "团队管理 <团队名> 删除成员 <区服> <角色名>\n"
        "团队管理 <团队名> 重置特征码\n"
        "团队管理 <团队名> 删除团队\n"
        "团队管理 <团队名> 删除团队 确认\n"
        "确认删除 <团队名>\n"
        "说明：团队按发起命令 QQ 名下团队名查找；绑定成员最多 25 个，同团队内同区服同角色重复绑定会覆盖原记录。"
    )


def list_owned_teams(creator_id: int) -> str:
    teams = _owned_teams(creator_id)
    if not teams:
        return "当前账号名下暂无团队。\n可在群内发送：注册团队 <团队名>"

    lines = [f"我的团队：共 {len(teams)} 个"]
    for index, team in enumerate(teams, start=1):
        members = list(team.members or [])
        lines.append(
            f"{index}. {team.team_name} "
            f"成员 {len(members)}/{TEAM_HEALTH_CAPACITY} "
            f"注册群 {team.group_id} "
            f"特征码 {team.feature_code} "
            f"更新 {_format_time(team.update_time)}"
        )
    lines.append("查看详情：团队管理 <团队名> 状态")
    return "\n".join(lines)


def remember_delete_team_confirmation(user_id: int, team_name: str) -> None:
    _cleanup_delete_team_confirmations()
    _PENDING_DELETE_TEAMS[_delete_team_confirm_key(user_id, team_name)] = Time().raw_time


def consume_delete_team_confirmation(user_id: int, team_name: str) -> str | None:
    key = _delete_team_confirm_key(user_id, team_name)
    timestamp = _PENDING_DELETE_TEAMS.pop(key, None)
    if timestamp is None:
        return "没有待确认的删除团队操作，请先发送：团队管理 <团队名> 删除团队"
    if Time().raw_time - int(timestamp) > DELETE_TEAM_CONFIRM_TTL:
        return "删除团队确认已过期，请重新发起命令。"
    return None


def prepare_delete_team_confirmation(creator_id: int, team_name: str) -> str:
    team_name = _normalize_team_name(team_name)
    team = _owned_team(creator_id, team_name)
    if team is None:
        return "未找到你名下的对应团队。"
    remember_delete_team_confirmation(creator_id, team_name)
    return (
        f"即将删除团队「{team.team_name}」及其全部成员绑定数据。\n"
        f"确认删除请回复：确认删除 {team.team_name}\n"
        f"也可直接发送：团队管理 {team.team_name} 删除团队 确认\n"
        "该确认 5 分钟内有效。"
    )


def delete_team(creator_id: int, team_name: str) -> str:
    team_name = _normalize_team_name(team_name)
    _PENDING_DELETE_TEAMS.pop(_delete_team_confirm_key(creator_id, team_name), None)
    team = _owned_team(creator_id, team_name)
    if team is None:
        return "未找到你名下的对应团队。"
    db.delete(RaidTeamHealth(), "creator_id = ? AND team_name = ?", int(creator_id), team_name)
    return f"已删除团队：{team.team_name}"


def delete_member(creator_id: int, team_name: str, role_name: str, server_arg: str | None = None, group_id: int | None = None) -> str:
    team = _owned_team(creator_id, _normalize_team_name(team_name))
    if team is None:
        return "未找到你名下的对应团队。"

    server = None
    if server_arg is not None:
        server = Server(server_arg, group_id).server
        if server is None:
            return PROMPT.ServerNotExist

    members: list[dict[str, Any]] = list(team.members or [])
    matches = [
        member
        for member in members
        if str(member.get("role_name")) == role_name
        and (server is None or str(member.get("server")) == server)
    ]
    if not matches:
        return "未找到对应成员。"
    if len(matches) > 1 and server is None:
        candidates = "\n".join(
            f"- {member.get('server')} {member.get('role_name')} ({member.get('kungfu_name')})"
            for member in matches
        )
        return (
            "检测到多个同名角色，请带区服删除：\n"
            f"{candidates}\n"
            f"参考格式：团队管理 {team.team_name} 删除成员 <区服> {role_name}"
        )

    target = matches[0]
    members = [
        member
        for member in members
        if not (
            str(member.get("server")) == str(target.get("server"))
            and str(member.get("role_name")) == str(target.get("role_name"))
        )
    ]
    team.members = members
    team.update_time = Time().raw_time
    db.save(team)
    return f"已删除成员：{target.get('role_name')}·{target.get('server')}"


def _rating_grade_class(grade: str) -> str:
    return (
        "grade-"
        + grade.lower()
        .replace("+", "-plus")
        .replace(" ", "-")
        .replace("/", "-")
    )


def _empty_recommendation() -> dict[str, str]:
    return {
        "text": "-",
        "icon": "",
    }


def _json_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _team_health_cache_key(
    member: dict[str, Any],
    equip: JX3PlayerAttribute,
    jcl_data: list[Any],
) -> dict[str, Any]:
    return {
        "version": TEAM_HEALTH_CACHE_VERSION,
        "global_role_id": int(member.get("global_role_id") or 0),
        "kungfu_id": int(member.get("kungfu_id") or 0),
        "equip_time": int(equip.timestamp),
        "equip_hash": _json_hash(jcl_data),
        "candidate_level": dict(TEAM_HEALTH_CANDIDATE_LEVEL),
    }


def _cached_team_health_row(member: dict[str, Any], cache_key: dict[str, Any]) -> dict[str, Any] | None:
    cache = member.get("health_cache")
    if not isinstance(cache, dict):
        return None
    if cache.get("version") != TEAM_HEALTH_CACHE_VERSION:
        return None
    if cache.get("key") != cache_key:
        return None
    row = cache.get("row")
    if not isinstance(row, dict):
        return None
    return dict(row)


def _team_health_rank_data(data: dict[str, Any]) -> dict[str, Any]:
    adaptive = _as_dict(data.get("adaptive_consumables"))
    return {
        "meta": _as_dict(data.get("meta")),
        "adaptive_consumables": {
            "status": adaptive.get("status"),
            "dps": adaptive.get("dps"),
        },
    }


def _record_team_health_rank(member: dict[str, Any], rank_data: dict[str, Any]) -> None:
    if not isinstance(rank_data, dict):
        return
    try:
        record_equipment_rating_rank(
            rank_data,
            str(member.get("role_name") or ""),
            str(member.get("server") or ""),
            str(member.get("role_id") or ""),
            int(member.get("global_role_id") or 0),
        )
    except Exception as exc:
        logger.warning(f"团队评级伤害排名记录失败：{exc}")


def _team_health_cache(
    cache_key: dict[str, Any],
    row: dict[str, Any],
    rank_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "version": TEAM_HEALTH_CACHE_VERSION,
        "key": cache_key,
        "row": row,
        "rank_data": rank_data or {},
        "cache_time": Time().raw_time,
    }


def _recommendation_item(item: dict[str, Any], *, with_delta: bool = False) -> dict[str, str]:
    name = str(item.get("name") or "").strip()
    if with_delta:
        delta_text = str(item.get("delta_text") or "").strip()
        if delta_text:
            name = f"{name}{delta_text}"
    return {
        "text": _escape(name or "-"),
        "icon": _escape(str(item.get("icon") or "").strip()),
    }


def _formation_recommendations(prepared_consumables: dict[str, Any] | None) -> list[dict[str, str]]:
    if not prepared_consumables:
        return [_empty_recommendation(), _empty_recommendation(), _empty_recommendation()]
    recommendations = []
    for item in prepared_consumables.get("formations") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        recommendations.append(_recommendation_item(item, with_delta=True))
    return (
        recommendations
        + [_empty_recommendation(), _empty_recommendation(), _empty_recommendation()]
    )[:3]


def _consumable_recommendations(prepared_consumables: dict[str, Any] | None) -> dict[str, list[dict[str, str]]]:
    recommendations = {
        "food": [_empty_recommendation()],
        "medicine": [_empty_recommendation()],
        "home": [_empty_recommendation()],
        "ingot": [_empty_recommendation()],
    }
    if not prepared_consumables:
        return recommendations
    for group in prepared_consumables.get("groups") or []:
        key = str(group.get("key") or "")
        if key not in recommendations:
            continue
        entries = [
            _recommendation_item(item)
            for item in group.get("entries") or []
            if isinstance(item, dict) and item.get("name")
        ]
        if entries:
            recommendations[key] = entries
    return recommendations


def _result_payload(member: dict[str, Any], data: dict[str, Any], equip: JX3PlayerAttribute) -> dict[str, Any]:
    summary = _as_dict(data.get("summary"))
    meta = _as_dict(data.get("meta"))
    kungfu_id = int(member.get("kungfu_id") or meta.get("kungfu_id") or 0)
    kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
    grade = str(summary.get("grade") or "D")
    prepared_consumables = _prepare_adaptive_consumables(data.get("adaptive_consumables"))
    tank = _prepare_tank_vitality_conversion(summary, kungfu)
    formation_top = _formation_recommendations(prepared_consumables)
    consumables = _consumable_recommendations(prepared_consumables)
    return {
        "ok": True,
        "sort_score": float(summary.get("total_score") or 0),
        "role_name": _escape(member.get("role_name")),
        "server": _escape(member.get("server")),
        "role_id": _escape(member.get("role_id")),
        "global_role_id": _escape(member.get("global_role_id")),
        "kungfu_name": _escape(kungfu.name or member.get("kungfu_name") or kungfu_id),
        "kungfu_icon": Path(kungfu.icon).as_uri(),
        "grade": _escape(grade),
        "grade_icon": _grade_icon(grade),
        "grade_class": _rating_grade_class(grade),
        "theme": RANK_THEMES.get(grade, RANK_THEMES["D"]),
        "equip_time": _format_time(equip.timestamp),
        "formation_top": formation_top,
        "food_recommendations": consumables["food"],
        "medicine_recommendations": consumables["medicine"],
        "home_recommendations": consumables["home"],
        "ingot_recommendations": consumables["ingot"],
        "tank_stacks": _escape(f"{tank['stacks']}层") if tank else "-",
    }


async def _rate_member(member: dict[str, Any]) -> dict[str, Any]:
    try:
        kungfu_id = int(member.get("kungfu_id") or 0)
        global_role_id = int(member.get("global_role_id") or 0)
        equip = await _rating_equip(global_role_id, kungfu_id)
        if equip is None:
            raise ValueError("未找到已绑定心法的可评级 PVE 装备数据")
        jcl_data = normalize_calculator_jcl_data(equip.equip_lines)
        cache_key = _team_health_cache_key(member, equip, jcl_data)
        cached_row = _cached_team_health_row(member, cache_key)
        if cached_row is not None:
            cache = _as_dict(member.get("health_cache"))
            rank_data = _as_dict(cache.get("rank_data"))
            _record_team_health_rank(member, rank_data)
            return {
                "row": cached_row,
                "cache": member.get("health_cache"),
                "cache_hit": True,
                "equip_time": int(equip.timestamp),
            }
        payload = {
            "kungfu_id": kungfu_id,
            "jcl_data": jcl_data,
            "role": {
                "name": str(member.get("role_name") or ""),
                "server": str(member.get("server") or ""),
                "global_role_id": global_role_id,
            },
            "candidate_level": dict(TEAM_HEALTH_CANDIDATE_LEVEL),
        }
        data = await _request_equipment_rating_data(payload)
        if isinstance(data, str):
            raise ValueError(data)
        rank_data = _team_health_rank_data(data)
        _record_team_health_rank(member, rank_data)
        row = _result_payload(member, data, equip)
        return {
            "row": row,
            "cache": _team_health_cache(cache_key, row, rank_data),
            "cache_hit": False,
            "equip_time": int(equip.timestamp),
        }
    except Exception as exc:
        kungfu_id = int(member.get("kungfu_id") or 0)
        kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
        return {
            "row": {
                "ok": False,
                "sort_score": -1,
                "role_name": _escape(member.get("role_name")),
                "server": _escape(member.get("server")),
                "role_id": _escape(member.get("role_id")),
                "global_role_id": _escape(member.get("global_role_id")),
                "kungfu_name": _escape(kungfu.name or member.get("kungfu_name") or kungfu_id),
                "kungfu_icon": Path(kungfu.icon).as_uri(),
                "grade": "未完成",
                "grade_icon": "",
                "grade_class": "grade-failed",
                "theme": RANK_THEMES["D"],
                "error": _escape(str(exc) or type(exc).__name__),
                "equip_time": _format_time(member.get("equip_time")),
                "formation_top": [
                    _empty_recommendation(),
                    _empty_recommendation(),
                    _empty_recommendation(),
                ],
                "food_recommendations": [_empty_recommendation()],
                "medicine_recommendations": [_empty_recommendation()],
                "home_recommendations": [_empty_recommendation()],
                "ingot_recommendations": [_empty_recommendation()],
                "tank_stacks": "-",
            },
            "cache": None,
            "cache_hit": False,
            "equip_time": int(member.get("equip_time") or 0),
        }


def _save_team_health_cache_results(team: RaidTeamHealth, members: list[dict[str, Any]], results: list[dict[str, Any]]) -> None:
    changed = False
    updated_members = []
    for member, result in zip(members, results):
        updated_member = dict(member)
        equip_time = int(result.get("equip_time") or 0)
        if equip_time and int(updated_member.get("equip_time") or 0) != equip_time:
            updated_member["equip_time"] = equip_time
            changed = True

        cache = result.get("cache")
        if isinstance(cache, dict):
            if updated_member.get("health_cache") != cache:
                updated_member["health_cache"] = cache
                changed = True
        elif "health_cache" in updated_member:
            updated_member.pop("health_cache", None)
            changed = True
        updated_members.append(updated_member)

    if not changed:
        return
    team.members = updated_members
    team.update_time = Time().raw_time
    db.save(team)


async def render_team_health_check(creator_id: int, team_name: str) -> str | ms:
    team = _owned_team(creator_id, _normalize_team_name(team_name))
    if team is None:
        return "未找到你名下的对应团队。"
    members: list[dict[str, Any]] = list(team.members or [])
    if not members:
        return "该团队暂无成员。"

    semaphore = asyncio.Semaphore(3)

    async def rate_with_limit(member: dict[str, Any]) -> dict[str, Any]:
        async with semaphore:
            return await _rate_member(member)

    results = await asyncio.gather(*(rate_with_limit(member) for member in members))
    _save_team_health_cache_results(team, members, results)
    sorted_results = sorted(
        enumerate(results),
        key=lambda item: (-float(item[1]["row"].get("sort_score", -1)), item[0]),
    )
    rows = [item["row"] for _, item in sorted_results]
    ok_count = sum(1 for row in rows if row.get("ok"))
    cache_hit_count = sum(1 for item in results if item.get("cache_hit"))
    refreshed_count = sum(1 for item in results if item.get("cache") and not item.get("cache_hit"))
    html_source = Template(read(TEAM_HEALTH_TEMPLATE)).render(
        font=Path(build_path(ASSETS, ["font", "PingFangSC-Medium.otf"])).as_uri(),
        team_name=_escape(team.team_name),
        member_count=len(members),
        ok_count=ok_count,
        cache_hit_count=cache_hit_count,
        refreshed_count=refreshed_count,
        capacity=TEAM_HEALTH_CAPACITY,
        generated_at=Time().format("%m-%d %H:%M"),
        rows=rows,
    )
    return await generate(
        html_source,
        ".team-health-canvas",
        segment=True,
        viewport={"width": 2520, "height": 2400},
    )
