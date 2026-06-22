from typing import Any
import html

from jinja2 import Template

from src.config import Config
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.server import Server
from src.const.path import ASSETS, build_path
from src.const.prompts import PROMPT
from src.utils.database.attributes import JX3PlayerAttribute
from src.utils.database.player import search_player
from src.utils.generate import generate
from src.utils.network import Request
from src.templates import get_saohua

from ._template import therapy_panel_template


THERAPY_KUNGFU_IDS = {10080, 10028, 10176, 10448, 10626}


async def _resolve_therapy_equip(global_role_id: int) -> JX3PlayerAttribute | None:
    equip = await JX3PlayerAttribute.from_database(global_role_id, "HPSPVE", False)
    if equip is not None:
        return equip

    all_equips = await JX3PlayerAttribute.from_database(global_role_id, "", True)
    if not all_equips:
        return None
    therapy_equips = [
        item
        for item in all_equips
        if item.tag == "PVE" and int(item.kungfu_id) in THERAPY_KUNGFU_IDS
    ]
    if not therapy_equips:
        return None
    return max(therapy_equips, key=lambda item: item.timestamp)


async def therapy_panel(server: str, role_name: str) -> Any:
    def format_skill_name(name: Any) -> str:
        skill_name = html.escape(str(name or "-")).replace("[", "<br>[", 1)
        if skill_name.startswith("<br>"):
            return skill_name[4:]
        return skill_name

    def format_number(value: Any, decimals: int = 0, percent: bool = False) -> str:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return "-"
        if percent:
            return f"{number:.{decimals}f}%"
        if decimals > 0:
            return f"{number:,.{decimals}f}"
        return f"{int(round(number)):,}"

    def format_coefficient(value: Any) -> str:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return html.escape(str(value)) if value not in (None, "") else "-"
        return f"{number:.4f}".rstrip("0").rstrip(".")

    def skill_rows(skills: list[dict[str, Any]], theme_color: str) -> str:
        rows: list[str] = []
        max_expected = max(
            (float(skill.get("expected_heal") or skill.get("heal") or 0) for skill in skills),
            default=0,
        )
        for skill in skills:
            icon_id = int(skill.get("icon_id") or 0)
            icon = f"https://icon.jx3box.com/icon/{icon_id}.png" if icon_id else ""
            icon_html = f'<img src="{icon}">' if icon else ""
            try:
                width = float(skill.get("expected_heal") or skill.get("heal") or 0) / max_expected * 100 if max_expected else 0
            except (TypeError, ValueError, ZeroDivisionError):
                width = 0
            skill_name = format_skill_name(skill.get("name"))
            coefficient = format_coefficient(skill.get("coefficient"))
            rows.append(
                f"""
                <div class="skill-card">
                    <div class="skill-head">
                        <div class="skill-icon">{icon_html}</div>
                        <div class="skill-name">{skill_name}</div>
                    </div>
                    <div class="skill-coefficient">系数 {coefficient}</div>
                    <div class="skill-stats">
                        <div><span>普通</span><b>{format_number(skill.get("heal"))}</b></div>
                        <div><span>期望</span><b>{format_number(skill.get("expected_heal"))}</b></div>
                        <div><span>会心</span><b>{format_number(skill.get("critical_heal"))}</b></div>
                    </div>
                    <div class="bar"><div style="width: {max(0, min(width, 100)):.2f}%; background: {theme_color}"></div></div>
                </div>
                """
            )
        return "\n".join(rows) or '<div class="empty">暂无技能数据</div>'

    def skill_card_width(skills: list[dict[str, Any]]) -> int:
        max_chars = 0
        for skill in skills:
            for line in format_skill_name(skill.get("name")).split("<br>"):
                max_chars = max(max_chars, len(line))
        return max(176, min(320, max_chars * 16 + 74))

    player_info = await search_player(role_name=role_name, server_name=server)
    if player_info.roleId == "" or player_info.globalRoleId == "":
        return PROMPT.PlayerNotExist

    await JX3PlayerAttribute.from_tuilan(player_info.roleId, player_info.serverName, player_info.globalRoleId)
    equip = await _resolve_therapy_equip(int(player_info.globalRoleId))
    if equip is None:
        return PROMPT.EquipNotFound
    if equip.kungfu_id not in THERAPY_KUNGFU_IDS:
        kungfu_name = Kungfu.with_internel_id(equip.kungfu_id, convert_to_pc=True).name or str(equip.kungfu_id)
        return f"治疗面板仅支持治疗心法，当前识别为：{kungfu_name}"

    try:
        result = (
            await Request(
                f"{Config.jx3.api.calculator_url}/calculate_therapy",
                params={"kungfu_id": equip.kungfu_id, "jcl_data": equip.equip_lines},
            ).post(timeout=30)
        ).json()
    except Exception:
        return "治疗面板计算失败，请确认 calculator 服务可用后重试！"
    if not isinstance(result, dict):
        return "治疗面板计算失败：calculator 返回数据格式有误。"
    if result.get("code") != 200:
        return "治疗面板计算失败：" + str(result.get("msg", "calculator 返回错误"))

    raw_data = result.get("data")
    data: dict[str, Any] = raw_data if isinstance(raw_data, dict) else result
    raw_attributes = data.get("attributes")
    attributes: dict[str, Any] = raw_attributes if isinstance(raw_attributes, dict) else {}
    raw_skills = data.get("skills")
    skills: list[dict[str, Any]] = (
        [skill for skill in raw_skills if isinstance(skill, dict)]
        if isinstance(raw_skills, list)
        else []
    )
    kungfu_id = int(data.get("kungfu_id") or equip.kungfu_id)
    kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
    theme_color = kungfu.color if kungfu.id != 10821 else "#A18DE3"
    attr_cards = [
        ("根骨", format_number(attributes.get("MainAttrValue"))),
        ("基础治疗量", format_number(attributes.get("BaseTherapy"))),
        ("最终治疗量", format_number(attributes.get("FinalTherapy"))),
        ("会心", format_number(attributes.get("CriticalPercent"), 2, True)),
        ("会心效果", format_number(attributes.get("CriticalDamagePercent"), 2, True)),
        ("加速", format_number(attributes.get("Haste"))),
    ]
    attr_html = "\n".join(
        f'<div class="item"><span>{html.escape(label)}</span><span>{html.escape(value)}</span></div>'
        for label, value in attr_cards
    )
    html_source = Template(therapy_panel_template).render(
        font=build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"]),
        theme_color=theme_color,
        kungfu_icon=kungfu.icon,
        role_name=html.escape(str(player_info.roleName or player_info.roleId or "-")),
        server_name=html.escape(str(Server(player_info.serverName).server or player_info.serverName or "-")),
        kungfu_name=html.escape(str(kungfu.name or kungfu_id)),
        score=format_number(data.get("score")),
        attr_html=attr_html,
        skill_rows=skill_rows(skills, theme_color),
        skill_card_width=skill_card_width(skills),
        saohua=get_saohua(),
    )
    return await generate(html_source, ".therapy-panel", False, segment=True, full_screen=True)
