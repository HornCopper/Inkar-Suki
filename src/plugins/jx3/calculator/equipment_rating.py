from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Template
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from src.config import Config
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.server import Server
from src.const.path import ASSETS, TEMPLATES, build_path
from src.const.prompts import PROMPT
from src.utils.database.attributes import JX3PlayerAttribute, TabCache, Talent
from src.utils.database.constant import (
    CRITICAL_DAMAGE_DIVISOR,
    CRITICAL_DIVISOR,
    OVERCOME_DIVISOR,
    STRAIN_DIVISOR,
)
from src.utils.database.player import get_uid_data, search_player
from src.utils.file import read
from src.utils.generate import generate
from src.utils.network import Request


equipment_rating_matcher = on_command(
    "jx3_equipment_rating",
    aliases={"装备评级"},
    priority=5,
    force_whitespace=True,
)

RANK_ICON_FILES = {
    "ACE": "rank_ace.png",
    "S+": "rank_s_plus.png",
    "S": "rank_s.png",
    "A": "rank_a.png",
    "B": "rank_b.png",
    "C": "rank_c.png",
    "D": "rank_d.png",
}


def _asset_uri(*parts: str) -> str:
    return Path(build_path(ASSETS, list(parts))).as_uri()


SLOT_DISPLAY_ORDER = [4, 3, 8, 12, 10, 11, 5, 9, 6, 7, 2, 0]
SLOT_NAME_OVERRIDES = {"上衣": "衣服"}
MAIN_ATTR_LABELS = {
    "atSpiritBase": "根骨",
    "atStrengthBase": "力道",
    "atAgilityBase": "身法",
    "atSpunkBase": "元气",
    "atVitalityBase": "体质",
}


def _to_float(value: Any, default: float = 0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _format_number(value: Any) -> str:
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return "0"


def _format_plain_int(value: Any) -> str:
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return "0"


def _format_signed(value: Any) -> str:
    try:
        return f"{int(float(value)):+,}"
    except (TypeError, ValueError):
        return "+0"


def _format_percent(value: Any) -> str:
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "0.0%"


def _percent_from_rating(value: Any, divisor: float, base: float = 0) -> str:
    return _format_percent((_to_float(value) / divisor + base) * 100)


def _haste_level(value: Any) -> int:
    haste = _to_float(value)
    if haste < 206:
        return 0
    if haste < 9232:
        return 1
    if haste < 19285:
        return 2
    if haste < 30158:
        return 3
    if haste < 42057:
        return 4
    return 5


def _grade_icon(grade: Any) -> str:
    return _asset_uri("image", "jx3", "equipment_rating", RANK_ICON_FILES.get(str(grade), "rank_d.png"))


def _attr_text(attributes: Any) -> str:
    if isinstance(attributes, list):
        return " ".join([str(item) for item in attributes if item])
    if isinstance(attributes, str):
        return attributes
    return ""


def _equip_icon(detail: dict[str, Any]) -> str:
    try:
        icon_id, _ = TabCache.get_icon_for_equip(int(detail.get("ui_id")))
    except Exception:
        icon_id = 1434
    return f"https://icon.jx3box.com/icon/{icon_id}.png"


def _quality_class(detail: dict[str, Any]) -> str:
    if _to_float(detail.get("quality")) >= 5:
        return "quality5"
    return "quality4"


def _prepare_slots(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prepared = []
    order = {location: index for index, location in enumerate(SLOT_DISPLAY_ORDER)}
    for slot in sorted(slots, key=lambda item: order.get(int(item.get("location_code", 99)), 99)):
        rating = slot.get("rating")
        current = slot.get("current") or {}
        best = slot.get("best") or {}
        location_name = SLOT_NAME_OVERRIDES.get(slot.get("location_name"), slot.get("location_name", ""))
        row = {
            **slot,
            "location_name": location_name,
            "current": {
                **current,
                "icon": _equip_icon(current),
                "level_text": _format_plain_int(current.get("level")),
                "attribute_text": _attr_text(current.get("attribute")),
                "quality_class": _quality_class(current),
            },
            "best": {
                **best,
                "icon": _equip_icon(best),
                "level_text": _format_plain_int(best.get("level")),
                "attribute_text": _attr_text(best.get("attribute")),
                "quality_class": _quality_class(best),
            },
            "is_rated": rating is not None,
            "grade_icon": "",
            "score_text": "--",
            "best_note": "",
            "has_haste_adjustment": False,
        }
        if rating is not None:
            grade = str(rating.get("grade", "D"))
            best_diff = _to_float(best.get("dps")) - _to_float(rating.get("current_dps"))
            adjustment = slot.get("haste_adjustment") or {}
            row.update(
                {
                    "grade_icon": _grade_icon(grade),
                    "score_text": str(rating.get("display_score", 0)),
                    "best_note": f"最优 {best.get('name', '候选装备')}: {_format_signed(best_diff)}",
                    "has_haste_adjustment": bool(adjustment.get("applied")),
                }
            )
        prepared.append(row)
    return prepared


def _prepare_attributes(summary: dict[str, Any], kungfu: Kungfu) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    attributes = summary.get("attributes") or {}
    main_attr_key = attributes.get("MainAttrKey")
    main_attr_label = MAIN_ATTR_LABELS.get(main_attr_key, "主属性")
    role_info = [
        {"label": "门派", "value": kungfu.school or "-"},
        {"label": "心法", "value": kungfu.name or "-"},
        {"label": "主属性", "value": main_attr_label},
        {"label": "目标", "value": "134级木桩"},
    ]
    basic_attrs = [
        {"label": "装分", "value": _format_number(summary.get("current_score"))},
        {"label": "基础攻击", "value": _format_number(attributes.get("BaseAttack"))},
        {"label": "面板攻击", "value": _format_number(attributes.get("FinalAttack"))},
        {"label": main_attr_label, "value": _format_number(attributes.get("MainAttrValue"))},
    ]
    detail_attrs = [
        {"label": "会心", "value": _percent_from_rating(attributes.get("Critical"), CRITICAL_DIVISOR)},
        {"label": "会效", "value": _percent_from_rating(attributes.get("CriticalDamage"), CRITICAL_DAMAGE_DIVISOR, 1.75)},
        {"label": "破防", "value": _percent_from_rating(attributes.get("Overcome"), OVERCOME_DIVISOR)},
        {"label": "无双", "value": _percent_from_rating(attributes.get("Strain"), STRAIN_DIVISOR)},
        {"label": "破招", "value": _format_number(attributes.get("Surplus"))},
        {"label": "加速", "value": f"{_format_number(attributes.get('Haste'))} / {_haste_level(attributes.get('Haste'))}"},
    ]
    return role_info, basic_attrs, detail_attrs


def _prepare_talents(talents: Any) -> list[dict[str, str]]:
    prepared = []
    for talent_id in talents or []:
        try:
            talent = Talent(int(talent_id))
        except Exception:
            continue
        prepared.append({"name": talent.name, "icon": talent.icon})
    return prepared


async def render_equipment_rating_image(data: dict[str, Any], role_name: str, server_name: str):
    meta = data["meta"]
    summary = data["summary"]
    kungfu = Kungfu.with_internel_id(meta["kungfu_id"])
    theme_color = kungfu.color if kungfu.name else "#4f6f87"
    role_info, basic_attrs, detail_attrs = _prepare_attributes(summary, kungfu)
    battle_time = _to_float(summary.get("battle_time"))
    haste_level = _haste_level(summary.get("current_haste"))
    summary_view = {
        **summary,
        "current_dps_text": _format_number(summary.get("current_dps")),
        "current_score_text": _format_number(summary.get("current_score")),
        "total_score_text": summary.get("display_total_score_text", f"{summary.get('display_total_score', 0):.1f}"),
        "grade_icon": _grade_icon(summary.get("grade", "D")),
        "battle_time_text": f"{battle_time:.1f}秒",
        "haste_level_text": f"{haste_level}段",
    }
    chips = [
        meta.get("loop_name", "评级专用循环"),
        f"{meta.get('jcl', {}).get('weapon', '')}{meta.get('jcl', {}).get('haste', '')}",
        meta.get("income_name", "默认增益"),
        summary_view["haste_level_text"],
        summary_view["battle_time_text"],
    ]
    html = Template(
        read(build_path(TEMPLATES, ["jx3", "equipment_rating.html"]))
    ).render(
        font=Path(build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"])).as_uri(),
        theme_color=theme_color,
        role_name=role_name or "未命名配装",
        server_name=server_name,
        kungfu_name=kungfu.name or str(meta["kungfu_id"]),
        kungfu_icon=Path(kungfu.icon).as_uri(),
        meta=meta,
        summary=summary_view,
        role_info=role_info,
        basic_attrs=basic_attrs,
        detail_attrs=detail_attrs,
        slots=_prepare_slots(data["slots"]),
        talents=_prepare_talents(summary.get("talents")),
        warnings=data.get("warnings", []),
        chips=[chip for chip in chips if chip],
    )
    return await generate(
        html,
        ".rating-canvas",
        segment=True,
        wait_for_network=True,
        viewport={"width": 1220, "height": 1800},
    )


@equipment_rating_matcher.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        matcher.stop_propagation()
        return
    arg = args.extract_plain_text().strip().split()
    if len(arg) != 3:
        await equipment_rating_matcher.finish(PROMPT.ArgumentCountInvalid + "\n参考格式：装备评级 <服务器> <角色> <心法>")

    server = Server(arg[0], event.group_id).server
    role_id = arg[1]
    kungfu_id = Kungfu(arg[2]).id
    if server is None:
        await equipment_rating_matcher.finish(PROMPT.ServerNotExist)
    if kungfu_id is None:
        await equipment_rating_matcher.finish(PROMPT.KungfuNotExist)

    player_data = await search_player(role_name=role_id, role_id=role_id, server_name=server, local_lookup=True)
    if player_data.roleId == "":
        player_data = await get_uid_data(role_id=role_id, server=server, msg=False)
    if player_data.roleId == "":
        await equipment_rating_matcher.finish(PROMPT.PlayerNotExist)

    await JX3PlayerAttribute.from_tuilan(player_data.roleId, player_data.serverName, player_data.globalRoleId)
    current_equip = await JX3PlayerAttribute.from_database(int(player_data.globalRoleId), all=True)
    if current_equip is None:
        await equipment_rating_matcher.finish(PROMPT.EquipNotFound)
    target_equip = next((equip for equip in current_equip if equip.kungfu_id == kungfu_id), None)
    if target_equip is None:
        await equipment_rating_matcher.finish("未找到该心法对应的装备，请先提交或查询该心法装备后重试。")

    payload = {
        "kungfu_id": int(kungfu_id),
        "jcl_data": target_equip.equip_lines,
        "role": {
            "name": player_data.roleName,
            "server": player_data.serverName,
            "global_role_id": int(player_data.globalRoleId),
        },
        "candidate_level": {
            "min": 32500,
            "max": 43000,
        },
    }
    try:
        response = await Request(f"{Config.jx3.api.calculator_url}/equipment_rating", params=payload).post(timeout=300)
        result = response.json()
    except Exception as exc:
        await equipment_rating_matcher.finish(f"装备评级计算失败：{exc}")

    if result.get("code") != 200:
        await equipment_rating_matcher.finish(result.get("msg", "装备评级计算失败。"))

    await equipment_rating_matcher.finish(
        await render_equipment_rating_image(result["data"], player_data.roleName, player_data.serverName)
    )
