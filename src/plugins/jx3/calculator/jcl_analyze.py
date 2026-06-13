from typing import Any, Literal
from collections import defaultdict
import html
import math
from jinja2 import Template
from httpx import AsyncClient

from src.config import Config
from src.const.path import ASSETS, TEMPLATES
from src.const.jx3.kungfu import Kungfu
from src.utils.file import read
from src.utils.analyze import sort_dict_list
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import SimpleHTML, HTMLSourceCode, get_saohua

from src.utils.database import rank_db as db
from src.utils.database.classes import CQCRank, THRRank

from ._template import (
    bla_template_body,

    fal_table_head,
    fal_template_body,
    
    yxc_table,
    hps_detail_template_body_main,
    hps_detail_template_body_sub,

    rod_table_head,
    rod_template_body,
    rod_css,

    asn_qte_table,
    asn_qte_template_body_main,

    lgz_table,
    lgz_detail_template_body_main,
    lgz_detail_template_body_sub,

    lnx_template_body
)

def save_data(data: dict[str, dict[str, int | str]], value_type: bool, rank_key: Literal["THR", "CQC"]) -> None:
    """
    value_type(bool): `1/True` for dps, `0/False` for hps
    """
    if rank_key == "THR":
        rank_model = THRRank
    else:
        rank_model = CQCRank
    key = "damage" if value_type else "health"
    for role_full_name, role_data in data.items():
        role_name, server_name = role_full_name.split("·")
        kungfu_id = int(role_data["kungfu_id"])
        total_damage = 0
        total_health = 0
        damage_per_second = 0
        health_per_second = 0
        if value_type:
            total_damage = role_data[f"total_{key}"]
            damage_per_second = role_data[f"{key}_per_second"]
        else:
            total_health = role_data[f"total_{key}"]
            health_per_second = role_data[f"{key}_per_second"]
        to_judge_value = total_damage if value_type else total_health
        current_record: CQCRank | THRRank | Any = db.where_one(
            rank_model(),
            f"role_name = ? AND server_name = ? AND total_{key} = ?",
            role_name, server_name, to_judge_value,
            default=None
        )
        if current_record is not None:
            continue
        new_data = rank_model(
            role_name = role_name,
            server_name = server_name,
            kungfu_id = kungfu_id
        )
        if value_type:
            setattr(new_data, f"total_{key}", total_damage)
            setattr(new_data, f"{key}_per_second", damage_per_second)
        else:
            setattr(new_data, f"total_{key}", total_health)
            setattr(new_data, f"{key}_per_second", health_per_second)
        db.save(new_data)
            
# Chi Qing Chuan
async def CQCAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/cqc_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()

    final_dps = []
    final_hps = []

    for player_name, player_data in data["data"][0].items():
        if anonymous:
            player_name = "匿名玩家"
        kungfu: Kungfu = Kungfu.with_internel_id(int(player_data["kungfu_id"]))
        final_dps.append(
            Template(bla_template_body).render(
                icon = kungfu.icon,
                name = player_name,
                rdps = "{:,}".format(int(player_data["total_damage"])),
                display = str(round(player_data["total_damage"] / list(data["data"][0].values())[0]["total_damage"], 4) * 100),
                color = kungfu.color,
                percent = "{:,}".format(int(player_data['damage_per_second']))
            )
        )

    for player_name, player_data in data["data"][1].items():
        if anonymous:
            player_name = "匿名玩家"
        kungfu: Kungfu = Kungfu.with_internel_id(int(player_data["kungfu_id"]))
        final_hps.append(
            Template(bla_template_body.replace("dps-num", "hps-num")).render(
                icon = kungfu.icon,
                name = player_name,
                rdps = "{:,}".format(int(player_data["total_health"])),
                display = str(round(player_data["total_health"] / list(data["data"][1].values())[0]["total_health"], 4) * 100),
                color = kungfu.color,
                percent = "{:,}".format(int(player_data['health_per_second']))
            )
        )
    try:
        save_data(data["data"][0], True, "CQC")
        save_data(data["data"][1], False, "CQC")
    except Exception:
        pass

    html = str(
        SimpleHTML(
            "jx3",
            "cqc_dps",
            title = "Inkar Suki 池清川P2战斗分析",
            battle_time = str(data["battle_time"]) + "s",
            dps_stastic = "\n".join(final_dps),
            hps_stastic = "\n".join(final_hps),
            saohua = get_saohua(),
            font = ASSETS + "/font/PingFangSC-Semibold.otf"
        )
    )
    dps_image = await generate(html, ".container", segment=True)
    return dps_image

# First Attacking List
async def FALAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/fal_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    tables = []
    for each_record in data["data"]:
        releaser_name = each_record["releaser_name"]
        # if anonymous:
        #     releaser_name = "匿名玩家"
        tables.append(
            Template(fal_template_body).render(
                time = Time(each_record["time"]).format("%H:%M:%S"),
                releaser = releaser_name + "<br>（" + str(each_record["releaser_id"]) + "）",
                target = each_record["target_name"] + "<br>（" + str(each_record["target_id"]) + "/" + str(each_record["target_template_id"]) + "）",
                skill = str(each_record["skill_id"])
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = "开怪统计",
            table_head = fal_table_head,
            table_body = "\n".join(tables)
        )
    )
    image = await generate(html, ".container", segment=True)
    return image  

# Yin Xue Chen
async def YXCAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/yxc_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    tables = []
    final_tables = []
    for each_record in data["data"]:
        if each_record == {}:
            final_tables.append(
                Template(yxc_table).render(
                    tables = "\n".join(tables)
                )
            )
            tables = []
            continue
        player_name = each_record["name"]
        if anonymous:
            player_name = "匿名玩家"
        tables.append(
            Template(hps_detail_template_body_main).render(
                icon=Kungfu.with_internel_id(int(each_record["kungfu_id"]), True).icon,
                name=player_name,
                value=each_record["value"]
            )
        )
        skills = dict(sorted(each_record["skills"].items(), key=lambda item: sum(item[1]), reverse=True))
        for skill_name, skill_values in skills.items():
            tables.append(
                Template(hps_detail_template_body_sub).render(
                    name = skill_name,
                    count = len(skill_values),
                    value = sum(skill_values),
                    percent = str(round(sum(skill_values) / each_record["value"] * 100, 2)) + "%"
                )
            )
    html = Template(
        read(TEMPLATES + "/jx3/health_detail.html")
    ).render(
        font = ASSETS + "/font/PingFangSC-Semibold.otf",
        tables = "\n".join(final_tables),
        saohua = get_saohua(),
        function_name = "尹雪尘承伤统计"
    )
    image = await generate(html, ".container", segment=True)
    return image

# Reason of Death
async def RODAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/rod_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    tables = []
    for each_record in data["data"]:
        # if anonymous:
        #     releaser_name = "匿名玩家"
        remark = ""
        skills = []
        for each_skill in each_record["final_damages"]:
            time = Time(each_skill["time"]).format("%H:%M:%S")
            name = each_skill["name"]
            damage = each_skill["effective_damage"]
            skills.append(
                f"[{time}]<span style=\"text-decoration: underline;\">{name}</span>：{damage}"
            )
        tables.append(
            Template(rod_template_body).render(
                time = Time(each_record["time"]).format("%H:%M:%S"),
                icon = Kungfu.with_internel_id(each_record["kungfu_id"], True).icon,
                name = each_record["name"],
                skills = ("<br>".join(skills) or "好像没有吃技能呢？<br>可能是战斗开始前死亡或者杯水到期等。"),
                remark = remark
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = "重伤统计",
            table_head = rod_table_head,
            table_body = "\n".join(tables),
            additional_css=rod_css
        )
    )
    image = await generate(html, ".container", segment=True)
    return image

# Healing per Second
async def HPSAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/hps_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    if data["data"] is None:
        return "分析失败，请检查 JCL 是否完整？如有必要请联系作者！"
    tables = []
    final_tables = []
    boss_name = data["data"]["boss"]
    for value_type in ["absorb", "health"]:
        for each_record in sort_dict_list(data["data"]["values"], f"total_{value_type}")[::-1]:
            if each_record[f"total_{value_type}"] == 0:
                continue
            tables.append(
                Template(hps_detail_template_body_main).render(
                    icon=Kungfu.with_internel_id(int(each_record["kungfu_id"]), True).icon,
                    name=each_record["name"],
                    value=str(each_record[f"total_{value_type}"]) + "<br>" + str(int(each_record[f"total_{value_type}"] / data["data"]["battle_time"])) + (" HPS" if value_type == "health" else " APS")
                )
            )
            skills = each_record["skills"][value_type]
            for skill in skills:
                tables.append(
                    Template(hps_detail_template_body_sub).render(
                        name = skill["name"],
                        count = str(skill["count"]) + "（" + str(skill["critical"]) + "会心）",
                        value = skill["value"],
                        percent = str(round(skill["value"] / each_record[f"total_{value_type}"] * 100, 2)) + "%"
                    )
                )
        final_tables.append(
            Template(yxc_table).render(
                tables = "\n".join(tables)
            )
        )
        tables = []
    html = Template(
        read(TEMPLATES + "/jx3/health_detail.html")
    ).render(
        font = ASSETS + "/font/PingFangSC-Semibold.otf",
        tables = "\n".join(final_tables),
        saohua = get_saohua(),
        function_name = f"{boss_name} HPS APS 统计"
    )
    image = await generate(html, ".container", segment=True)
    return image

async def CALAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.calculator_url}/submit_jcl", json={"url": url, "name": file_name, "user_id": user_id}, timeout=600)
        data = resp.json()
    if data["code"] != 200:
        if data["status"] == -1:
            return "请检查 JCL 名称，无法解析！\n参考格式：CAL-莫问-19285-紫武-常规循环.jcl\nCAL-心法名-加速等级-紫武/橙武-循环名.jcl"
        elif data["status"] == -2:
            return "请检查心法名称，无法识别该心法名称！"
    else:
        return "导入成功！\n发送「偏好 计算器来源 自定义」可使用导入的循环；\n发送「偏好 计算器来源 公用」可恢复使用公开循环！"

LNX_DECAY_RATE = 0.3
LNX_MAGNETIC_BUFF_ID = 33480
LNX_MAGNETIC_BUFF_NAME = "磁雷弱化"
LNX_VULNERABLE_DAMAGE_LIMIT = 2_200_000.0
LNX_PIE_COLORS = [
    "#597aa8",
    "#d58b55",
    "#72a983",
    "#b56d93",
    "#8b78c5",
    "#c9a44f",
]
LNX_PIE_OTHER_COLOR = "#a8b2c1"
LNX_KUNGFU_SHORT_NAMES = {
    "傲血战意": "傲血",
    "铁牢律": "铁牢",
    "紫霞功": "紫霞",
    "太虚剑意": "太虚",
    "花间游": "花间",
    "离经易道": "离经",
    "云裳心经": "云裳",
    "冰心诀": "冰心",
    "毒经": "毒经",
    "补天诀": "补天",
    "易筋经": "易筋",
    "洗髓经": "洗髓",
    "问水诀": "问水",
    "山居问水剑": "问水",
    "山居问水剑·悟": "问水",
    "莫问": "莫问",
    "相知": "相知",
    "凌海诀": "凌海",
    "隐龙诀": "隐龙",
    "无方": "无方",
    "孤锋诀": "孤锋",
    "山海心诀": "山海",
}


def _lnx_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _lnx_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _lnx_safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _lnx_safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _lnx_entity_key(entity: dict[str, Any], default_name: str) -> str:
    entity_id = str(entity.get("id", "")).strip()
    name = str(entity.get("name") or default_name).strip()
    entity_type = str(entity.get("type") or "").strip()
    kungfu_id = str(entity.get("kungfu_id") or "").strip()
    if entity_id and entity_id != "0":
        return f"id:{entity_id}"
    return f"name:{name}|type:{entity_type}|kungfu:{kungfu_id}"


def _lnx_entity(raw_entity: Any, default_name: str, anonymous: bool = False) -> dict[str, Any]:
    entity = _lnx_dict(raw_entity)
    name = str(entity.get("name") or default_name).strip() or default_name
    entity_type = str(entity.get("type") or "").strip()
    display_name = "匿名玩家" if anonymous and entity_type == "玩家" else name
    kungfu_id = _lnx_safe_int(entity.get("kungfu_id"), 0)
    kungfu = Kungfu.with_internel_id(kungfu_id, True)
    return {
        "key": _lnx_entity_key(entity, default_name),
        "id": entity.get("id", ""),
        "name": name,
        "display_name": display_name,
        "type": entity_type,
        "kungfu_id": kungfu_id,
        "kungfu_name": kungfu.name or "",
        "icon": kungfu.icon,
    }


def _lnx_reduction_percent(reduction: Any) -> float:
    return _lnx_safe_float(_lnx_dict(reduction).get("percent"), 0.0)


def _lnx_is_magnetic_vulnerability(reduction: Any) -> bool:
    data = _lnx_dict(reduction)
    return (
        _lnx_safe_int(data.get("buff_id"), 0) == LNX_MAGNETIC_BUFF_ID
        or str(data.get("name") or "").strip() == LNX_MAGNETIC_BUFF_NAME
    ) and _lnx_reduction_percent(data) < 0


def _lnx_target_reductions(wave: dict[str, Any], anonymous: bool) -> dict[str, list[dict[str, Any]]]:
    reductions: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in _lnx_list(wave.get("damage_reductions_by_player")):
        item_data = _lnx_dict(item)
        target = _lnx_entity(item_data.get("player"), "未知目标", anonymous)
        reductions[target["key"]].extend(
            _lnx_dict(reduction)
            for reduction in _lnx_list(item_data.get("reductions"))
        )
    return reductions


def _lnx_vulnerability_multiplier(reductions: list[dict[str, Any]]) -> float:
    if any(_lnx_is_magnetic_vulnerability(reduction) for reduction in reductions):
        return 1.3
    return 1.0


def _lnx_restore_raw_damage(
    after_damage: float,
    vulnerability_multiplier: float,
    reductions: list[dict[str, Any]],
) -> tuple[float, float]:
    if after_damage <= 0:
        return 0.0, 0.0

    positive_percents = sorted(
        {
            percent
            for percent in (_lnx_reduction_percent(reduction) for reduction in reductions)
            if 0 < percent < 100
        },
        reverse=True,
    )
    for percent in [*positive_percents, 0.0]:
        denominator = vulnerability_multiplier * (1 - percent / 100)
        if denominator <= 0:
            continue
        raw_damage = after_damage / denominator
        if raw_damage * vulnerability_multiplier <= LNX_VULNERABLE_DAMAGE_LIMIT:
            return raw_damage, percent

    denominator = vulnerability_multiplier if vulnerability_multiplier > 0 else 1.0
    return min(after_damage / denominator, LNX_VULNERABLE_DAMAGE_LIMIT / denominator), 0.0


def _lnx_format_number(value: float) -> str:
    rounded = int(round(value))
    sign = "-" if rounded < 0 else ""
    amount = abs(rounded)
    if amount >= 10000:
        wan = amount / 10000
        if wan >= 100:
            return f"{sign}{wan:.0f}万"
        if wan >= 10:
            return f"{sign}{wan:.1f}万"
        return f"{sign}{wan:.2f}万"
    return f"{rounded:,}"


def _lnx_format_percent(value: float) -> str:
    if float(value).is_integer():
        return f"{int(value)}%"
    return f"{value:.1f}%"


def _lnx_role_html(entity: dict[str, Any]) -> str:
    name = html.escape(str(entity.get("display_name") or entity.get("name") or "未知来源"))
    icon = html.escape(str(entity.get("icon") or ""))
    entity_type = html.escape(str(entity.get("type") or ""))
    sub = f"<div class=\"muted\">{entity_type}</div>" if entity_type and entity_type != "玩家" else ""
    return f"<div class=\"role-cell\"><img src=\"{icon}\"><div>{name}{sub}</div></div>"


def _lnx_short_text(value: Any, limit: int = 5) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "…"


def _lnx_short_role_name(entity: dict[str, Any]) -> str:
    name = str(entity.get("display_name") or entity.get("name") or "未知来源").strip()
    name = name.split("·", 1)[0]
    name = name.split("@", 1)[0]
    return _lnx_short_text(name, 5)


def _lnx_short_kungfu_name(kungfu_name: Any) -> str:
    name = str(kungfu_name or "").strip()
    if not name:
        return ""
    if name in LNX_KUNGFU_SHORT_NAMES:
        return LNX_KUNGFU_SHORT_NAMES[name]
    for suffix in ("心经", "心诀", "战意", "剑意", "易道", "问水剑", "诀", "经", "功"):
        if name.endswith(suffix) and len(name) > len(suffix) + 1:
            return _lnx_short_text(name[:-len(suffix)], 3)
    return _lnx_short_text(name, 3)


def _lnx_chart_entity_label(entity: dict[str, Any]) -> str:
    role_name = _lnx_short_role_name(entity)
    kungfu_name = _lnx_short_kungfu_name(entity.get("kungfu_name"))
    if kungfu_name:
        return f"{kungfu_name} {role_name}"
    return role_name


def _lnx_table(headers: list[str], rows: list[list[str]], empty_text: str = "无数据", css_class: str = "") -> str:
    head = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    if not rows:
        body = f"<tr><td colspan=\"{len(headers)}\" class=\"muted\">{html.escape(empty_text)}</td></tr>"
    else:
        body = "\n".join(
            "<tr>" + "".join(cell for cell in row) + "</tr>"
            for row in rows
        )
    class_attr = f" class=\"{html.escape(css_class)}\"" if css_class else ""
    return f"<table{class_attr}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _lnx_stat() -> dict[str, Any]:
    return {
        "entity": {},
        "mitigation_raw": 0.0,
        "mitigation_weighted": 0.0,
        "heal_raw": 0.0,
        "heal_weighted": 0.0,
    }


def build_lnx_analysis_data(raw_data: Any, anonymous: bool = False) -> list[dict[str, Any]]:
    if isinstance(raw_data, dict) and "data" in raw_data:
        raw_data = raw_data["data"]
    phases: list[dict[str, Any]] = []
    for phase_order, phase_item in enumerate(_lnx_list(raw_data)):
        phase = _lnx_dict(phase_item)
        phase_index = _lnx_safe_int(phase.get("index"), phase_order + 1)
        waves: list[dict[str, Any]] = []
        phase_defaults: dict[str, float] = {}
        phase_entities: dict[str, dict[str, Any]] = {}

        for wave_order, wave_item in enumerate(_lnx_list(phase.get("waves"))):
            wave = _lnx_dict(wave_item)
            wave_index = _lnx_safe_int(wave.get("index"), wave_order + 1)
            reductions_by_target = _lnx_target_reductions(wave, anonymous)
            player_rows: list[dict[str, Any]] = []
            target_contexts: dict[str, dict[str, Any]] = {}

            for damage_item in _lnx_list(wave.get("damage_by_player")):
                damage_data = _lnx_dict(damage_item)
                target = _lnx_entity(damage_data.get("player"), "未知目标", anonymous)
                target_key = target["key"]
                reductions = reductions_by_target.get(target_key, [])
                effective_damage = max(0.0, _lnx_safe_float(damage_data.get("effective_damage")))
                absorbed_damage = max(0.0, _lnx_safe_float(damage_data.get("absorbed_damage")))
                after_damage = effective_damage + absorbed_damage
                vulnerability_multiplier = _lnx_vulnerability_multiplier(reductions)
                positive_percents = [
                    percent
                    for percent in (_lnx_reduction_percent(reduction) for reduction in reductions)
                    if 0 < percent < 100
                ]
                max_reduction_percent = max(positive_percents, default=0.0)
                raw_damage, selected_reduction_percent = _lnx_restore_raw_damage(
                    after_damage,
                    vulnerability_multiplier,
                    reductions,
                )
                vulnerable_damage = raw_damage * vulnerability_multiplier
                reduced_damage = max(0.0, vulnerable_damage - after_damage)
                vulnerability_added_damage = max(0.0, vulnerable_damage - raw_damage)
                selected_reductions = [
                    reduction
                    for reduction in reductions
                    if (
                        _lnx_reduction_percent(reduction) == selected_reduction_percent
                        and selected_reduction_percent > 0
                    )
                ]
                vulnerabilities = [
                    reduction
                    for reduction in reductions
                    if _lnx_is_magnetic_vulnerability(reduction)
                ]

                player_row = {
                    "entity": target,
                    "effective_damage": effective_damage,
                    "absorbed_damage": absorbed_damage,
                    "after_damage": after_damage,
                    "max_reduction_percent": max_reduction_percent,
                    "selected_reduction_percent": selected_reduction_percent,
                    "vulnerability_multiplier": vulnerability_multiplier,
                    "raw_damage": raw_damage,
                    "vulnerable_damage": vulnerable_damage,
                    "reduced_damage": reduced_damage,
                    "vulnerability_added_damage": vulnerability_added_damage,
                    "selected_reductions": selected_reductions,
                    "vulnerabilities": vulnerabilities,
                }
                player_rows.append(player_row)
                target_contexts[target_key] = player_row
                phase_entities[target_key] = target
                phase_defaults[target_key] = max(phase_defaults.get(target_key, 0.0), raw_damage)

            waves.append(
                {
                    "index": wave_index,
                    "source": wave,
                    "players": player_rows,
                    "wave_base_damage": max(
                        (player["vulnerable_damage"] for player in player_rows),
                        default=0.0,
                    ),
                    "target_reductions": reductions_by_target,
                    "target_contexts": target_contexts,
                }
            )

        terminal_wave = max((wave["index"] for wave in waves), default=0)
        phase_players: defaultdict[str, dict[str, Any]] = defaultdict(_lnx_stat)
        mitigation_buff_stats: dict[tuple[str, str, str, float], dict[str, Any]] = {}
        wave_summaries: list[dict[str, Any]] = []
        phase_mitigation_raw = 0.0
        phase_mitigation_weighted = 0.0
        phase_heal_raw = 0.0
        phase_heal_weighted = 0.0
        phase_absorb_raw = 0.0
        phase_absorb_weighted = 0.0

        for wave in waves:
            wave_index = wave["index"]
            current_terminal = max(terminal_wave, wave_index)
            time_weight = math.exp(-LNX_DECAY_RATE * (current_terminal - wave_index)) if current_terminal else 1.0
            source = wave["source"]
            wave_mitigation_raw = 0.0
            wave_heal_raw = 0.0
            wave_absorb_raw = 0.0

            for item in _lnx_list(source.get("damage_reductions_by_player")):
                item_data = _lnx_dict(item)
                target = _lnx_entity(item_data.get("player"), "未知目标", anonymous)
                target_key = target["key"]
                reductions = [
                    _lnx_dict(reduction)
                    for reduction in _lnx_list(item_data.get("reductions"))
                ]
                base_damage = _lnx_safe_float(wave.get("wave_base_damage"), 0.0)

                for reduction in reductions:
                    percent = _lnx_reduction_percent(reduction)
                    if percent <= 0:
                        continue
                    percent = min(percent, 100.0)
                    contribution = base_damage * percent / 100
                    weighted_contribution = contribution * time_weight
                    applier = _lnx_entity(reduction.get("applier"), "未知来源", anonymous)
                    applier_stat = phase_players[applier["key"]]
                    applier_stat["entity"] = applier
                    applier_stat["mitigation_raw"] += contribution
                    applier_stat["mitigation_weighted"] += weighted_contribution
                    wave_mitigation_raw += contribution

                    buff_id = str(reduction.get("buff_id") or "")
                    buff_name = str(reduction.get("name") or buff_id or "未知减伤")
                    buff_key = (applier["key"], buff_id, buff_name, percent)
                    if buff_key not in mitigation_buff_stats:
                        mitigation_buff_stats[buff_key] = {
                            "applier": applier,
                            "buff_id": buff_id,
                            "buff_name": buff_name,
                            "percent": percent,
                            "raw": 0.0,
                            "weighted": 0.0,
                            "targets": set(),
                            "count": 0,
                        }
                    buff_stat = mitigation_buff_stats[buff_key]
                    buff_stat["raw"] += contribution
                    buff_stat["weighted"] += weighted_contribution
                    buff_stat["targets"].add(target["display_name"])
                    buff_stat["count"] += 1

            for healer_item in _lnx_list(source.get("healers")):
                healer_data = _lnx_dict(healer_item)
                healer = _lnx_entity(healer_data, "未知来源", anonymous)
                contribution = max(0.0, _lnx_safe_float(healer_data.get("health")))
                weighted_contribution = contribution * time_weight
                healer_stat = phase_players[healer["key"]]
                healer_stat["entity"] = healer
                healer_stat["heal_raw"] += contribution
                healer_stat["heal_weighted"] += weighted_contribution
                wave_heal_raw += contribution

            for damage_item in _lnx_list(source.get("damage_by_player")):
                damage_data = _lnx_dict(damage_item)
                wave_absorb_raw += max(0.0, _lnx_safe_float(damage_data.get("absorbed_damage")))

            wave_mitigation_weighted = wave_mitigation_raw * time_weight
            wave_heal_weighted = wave_heal_raw * time_weight
            wave_absorb_weighted = wave_absorb_raw * time_weight
            phase_mitigation_raw += wave_mitigation_raw
            phase_mitigation_weighted += wave_mitigation_weighted
            phase_heal_raw += wave_heal_raw
            phase_heal_weighted += wave_heal_weighted
            phase_absorb_raw += wave_absorb_raw
            phase_absorb_weighted += wave_absorb_weighted

            wave_summaries.append(
                {
                    "index": wave_index,
                    "time_weight": time_weight,
                    "mitigation_raw": wave_mitigation_raw,
                    "mitigation_weighted": wave_mitigation_weighted,
                    "heal_raw": wave_heal_raw,
                    "heal_weighted": wave_heal_weighted,
                    "absorb_raw": wave_absorb_raw,
                    "absorb_weighted": wave_absorb_weighted,
                    "total_weighted": wave_mitigation_weighted + wave_heal_weighted + wave_absorb_weighted,
                }
            )

        player_rows = []
        for stat in phase_players.values():
            weighted_total = stat["mitigation_weighted"] + stat["heal_weighted"]
            raw_total = stat["mitigation_raw"] + stat["heal_raw"]
            if weighted_total <= 0 and raw_total <= 0:
                continue
            player_rows.append(
                {
                    **stat,
                    "weighted_total": weighted_total,
                    "raw_total": raw_total,
                }
            )
        player_rows.sort(key=lambda item: item["weighted_total"], reverse=True)

        mitigation_rows = [
            row for row in player_rows if row["mitigation_weighted"] > 0
        ]
        mitigation_rows.sort(key=lambda item: item["mitigation_weighted"], reverse=True)
        heal_rows = [
            row for row in player_rows if row["heal_weighted"] > 0
        ]
        heal_rows.sort(key=lambda item: item["heal_weighted"], reverse=True)
        buff_rows = list(mitigation_buff_stats.values())
        buff_rows.sort(key=lambda item: item["weighted"], reverse=True)
        wave_summaries.sort(key=lambda item: item["index"])

        phase_defaults_rows = [
            {
                "entity": phase_entities[key],
                "phase_default_raw_damage": value,
            }
            for key, value in phase_defaults.items()
        ]
        phase_defaults_rows.sort(key=lambda item: item["phase_default_raw_damage"], reverse=True)

        phases.append(
            {
                "phase_index": phase_index,
                "trigger_line": phase.get("trigger_line", ""),
                "wave_count": phase.get("wave_count", len(waves)),
                "terminal_wave": terminal_wave,
                "phase_player_defaults": phase_defaults_rows,
                "players": player_rows,
                "mitigation_players": mitigation_rows,
                "heal_players": heal_rows,
                "mitigation_buffs": buff_rows,
                "waves": wave_summaries,
                "totals": {
                    "mitigation_raw": phase_mitigation_raw,
                    "mitigation_weighted": phase_mitigation_weighted,
                    "heal_raw": phase_heal_raw,
                    "heal_weighted": phase_heal_weighted,
                    "absorb_raw": phase_absorb_raw,
                    "absorb_weighted": phase_absorb_weighted,
                    "weighted": phase_mitigation_weighted + phase_heal_weighted + phase_absorb_weighted,
                },
            }
        )
    return phases


def _lnx_bar_cell(value: float, max_value: float) -> str:
    ratio = 0.0 if max_value <= 0 else min(max(value / max_value, 0.0), 1.0)
    return (
        f"<td class=\"num contribution-bar\" style=\"--bar:{ratio * 100:.2f}%\">"
        f"<span>{_lnx_format_number(value)}</span>"
        "</td>"
    )


def _lnx_contribution_rows(rows: list[dict[str, Any]]) -> list[list[str]]:
    result = []
    max_total = max((_lnx_safe_float(row.get("weighted_total"), 0.0) for row in rows), default=0.0)
    max_mitigation = max((_lnx_safe_float(row.get("mitigation_weighted"), 0.0) for row in rows), default=0.0)
    max_heal = max((_lnx_safe_float(row.get("heal_weighted"), 0.0) for row in rows), default=0.0)
    for index, row in enumerate(rows, 1):
        result.append(
            [
                f"<td class=\"rank\">{index}</td>",
                f"<td>{_lnx_role_html(row['entity'])}</td>",
                _lnx_bar_cell(row["weighted_total"], max_total),
                _lnx_bar_cell(row["mitigation_weighted"], max_mitigation),
                _lnx_bar_cell(row["heal_weighted"], max_heal),
            ]
        )
    return result


def _lnx_single_contribution_rows(rows: list[dict[str, Any]], value_key: str) -> list[list[str]]:
    result = []
    max_value = max((_lnx_safe_float(row.get(value_key), 0.0) for row in rows), default=0.0)
    for index, row in enumerate(rows, 1):
        result.append(
            [
                f"<td class=\"rank\">{index}</td>",
                f"<td>{_lnx_role_html(row['entity'])}</td>",
                _lnx_bar_cell(row[value_key], max_value),
            ]
        )
    return result


def _lnx_buff_rows(rows: list[dict[str, Any]]) -> list[list[str]]:
    result = []
    max_weighted = max((_lnx_safe_float(row.get("weighted"), 0.0) for row in rows), default=0.0)
    for index, row in enumerate(rows, 1):
        target_count = len(row.get("targets", set()))
        result.append(
            [
                f"<td class=\"rank\">{index}</td>",
                f"<td>{_lnx_role_html(row['applier'])}</td>",
                f"<td>{html.escape(str(row['buff_name']))}</td>",
                f"<td class=\"num\">{_lnx_format_percent(row['percent'])}</td>",
                _lnx_bar_cell(row["weighted"], max_weighted),
                f"<td class=\"num muted\">{row['count']}次 / {target_count}人</td>",
            ]
        )
    return result


def _lnx_format_ratio(value: float) -> str:
    percent = value * 100
    return f"{percent:.1f}%" if percent < 10 else f"{percent:.0f}%"


def _lnx_pie_card(title: str, items: list[dict[str, Any]]) -> str:
    valid_items = [item for item in items if _lnx_safe_float(item.get("value"), 0.0) > 0]
    total = sum(_lnx_safe_float(item.get("value"), 0.0) for item in valid_items)
    if total <= 0:
        return f"""
        <div class="pie-card">
            <div class="pie-title">{html.escape(title)}</div>
            <div class="muted">无贡献数据</div>
        </div>
        """

    slice_rows = []
    guide_rows = []
    label_rows = []
    marker_id = f"lnx-rose-arrow-{id(valid_items)}"
    chart_width = 406.0
    chart_height = 265.0
    center_x = 203.0
    center_y = 132.0
    inner_radius = 16.0
    outer_radius = 78.0
    min_radius = 42.0
    gap_angle = 3.0
    slice_angle = 360.0 / len(valid_items)
    max_value = max((_lnx_safe_float(item.get("value"), 0.0) for item in valid_items), default=0.0)
    for index, item in enumerate(valid_items, 1):
        value = _lnx_safe_float(item.get("value"), 0.0)
        ratio = value / total if total else 0.0
        radius_ratio = math.sqrt(value / max_value) if max_value > 0 else 0.0
        radius = min_radius + (outer_radius - min_radius) * radius_ratio
        start_degree = -90.0 + (index - 1) * slice_angle + gap_angle / 2
        end_degree = -90.0 + index * slice_angle - gap_angle / 2
        start_angle = math.radians(start_degree)
        end_angle = math.radians(end_degree)
        mid_angle = math.radians((start_degree + end_degree) / 2)
        large_arc = 1 if end_degree - start_degree > 180 else 0
        outer_start_x = center_x + math.cos(start_angle) * radius
        outer_start_y = center_y + math.sin(start_angle) * radius
        outer_end_x = center_x + math.cos(end_angle) * radius
        outer_end_y = center_y + math.sin(end_angle) * radius
        inner_start_x = center_x + math.cos(start_angle) * inner_radius
        inner_start_y = center_y + math.sin(start_angle) * inner_radius
        inner_end_x = center_x + math.cos(end_angle) * inner_radius
        inner_end_y = center_y + math.sin(end_angle) * inner_radius
        label_x = center_x + math.cos(mid_angle) * 166
        label_y = center_y + math.sin(mid_angle) * 118
        label_x = min(max(label_x, 72), chart_width - 72)
        label_y = min(max(label_y, 26), chart_height - 26)
        label_to_center_x = center_x - label_x
        label_to_center_y = center_y - label_y
        half_label_width = 62.0
        half_label_height = 13.0
        edge_scale_x = half_label_width / abs(label_to_center_x) if abs(label_to_center_x) > 0.001 else float("inf")
        edge_scale_y = half_label_height / abs(label_to_center_y) if abs(label_to_center_y) > 0.001 else float("inf")
        edge_scale = min(edge_scale_x, edge_scale_y)
        line_start_x = label_x + label_to_center_x * edge_scale
        line_start_y = label_y + label_to_center_y * edge_scale
        line_end_x = center_x + math.cos(mid_angle) * (radius * 0.82)
        line_end_y = center_y + math.sin(mid_angle) * (radius * 0.82)
        line_vector_x = line_end_x - line_start_x
        line_vector_y = line_end_y - line_start_y
        line_length = max(math.hypot(line_vector_x, line_vector_y), 1.0)
        bend = 10.0 if index % 2 else -10.0
        control_x = (line_start_x + line_end_x) / 2 - line_vector_y / line_length * bend
        control_y = (line_start_y + line_end_y) / 2 + line_vector_x / line_length * bend
        guide_path = (
            f"M {line_start_x:.1f} {line_start_y:.1f} "
            f"Q {control_x:.1f} {control_y:.1f} {line_end_x:.1f} {line_end_y:.1f}"
        )
        slice_rows.append(
            "<g class=\"rose-slice-group\">"
            "<path class=\"rose-slice\" "
            f"d=\"M {inner_start_x:.1f} {inner_start_y:.1f} "
            f"L {outer_start_x:.1f} {outer_start_y:.1f} "
            f"A {radius:.1f} {radius:.1f} 0 {large_arc} 1 {outer_end_x:.1f} {outer_end_y:.1f} "
            f"L {inner_end_x:.1f} {inner_end_y:.1f} "
            f"A {inner_radius:.1f} {inner_radius:.1f} 0 {large_arc} 0 {inner_start_x:.1f} {inner_start_y:.1f} Z\" "
            f"fill=\"{item['color']}\" />"
            "</g>"
        )
        guide_rows.append(
            f"<path class=\"rose-guide-shadow\" d=\"{guide_path}\" />"
            f"<path class=\"rose-guide-line\" d=\"{guide_path}\" marker-end=\"url(#{marker_id})\" />"
        )
        icon = str(item.get("icon") or "").strip()
        icon_html = (
            f"<img src=\"{html.escape(icon)}\">"
            if icon else f"<span class=\"rose-label-dot\" style=\"background:{item['color']};\"></span>"
        )
        label_rows.append(
            "<span class=\"rose-entity-label\" "
            f"style=\"left:{label_x:.1f}px;top:{label_y:.1f}px;--label-color:{item['color']};\">"
            f"{icon_html}<span class=\"rose-entity-name\">{html.escape(str(item.get('chart_label') or item['label']))}</span>"
            f"<b>{_lnx_format_ratio(ratio)}</b></span>"
        )

    return f"""
    <div class="pie-card">
        <div class="pie-title">{html.escape(title)}</div>
        <div class="pie-body">
            <div class="pie-chart">
                <svg class="rose-chart" viewBox="0 0 {chart_width:.0f} {chart_height:.0f}" aria-hidden="true">
                    <defs>
                        <marker id="{marker_id}" viewBox="0 0 5 5" refX="4.6" refY="2.5" markerWidth="5" markerHeight="5" orient="auto">
                            <path d="M0,0 L5,2.5 L0,5 Z"></path>
                        </marker>
                    </defs>
                    <circle class="rose-backdrop" cx="{center_x:.1f}" cy="{center_y:.1f}" r="80"></circle>
                    {"".join(slice_rows)}
                    {"".join(guide_rows)}
                    <circle class="rose-core" cx="{center_x:.1f}" cy="{center_y:.1f}" r="15"></circle>
                </svg>
                {"".join(label_rows)}
            </div>
        </div>
    </div>
    """


def _lnx_pie_html(title: str, rows: list[dict[str, Any]], value_key: str) -> str:
    valid_rows = [row for row in rows if _lnx_safe_float(row.get(value_key), 0.0) > 0]
    total = sum(_lnx_safe_float(row.get(value_key), 0.0) for row in valid_rows)
    items: list[dict[str, Any]] = []
    top_rows = valid_rows[:5]
    for index, row in enumerate(top_rows):
        value = _lnx_safe_float(row.get(value_key), 0.0)
        items.append(
            {
                "label": str(row["entity"].get("display_name") or "未知来源"),
                "chart_label": _lnx_chart_entity_label(row["entity"]),
                "icon": str(row["entity"].get("icon") or ""),
                "value": value,
                "color": LNX_PIE_COLORS[index % len(LNX_PIE_COLORS)],
            }
        )

    other_value = max(0.0, total - sum(item["value"] for item in items))
    if other_value > 0:
        items.append({"label": "其他", "chart_label": "其他", "value": other_value, "color": LNX_PIE_OTHER_COLOR})

    return _lnx_pie_card(title, items)


def _lnx_absorb_pie_html(phase: dict[str, Any]) -> str:
    weighted_total = max(0.0, _lnx_safe_float(_lnx_dict(phase.get("totals")).get("weighted"), 0.0))
    absorb = max(0.0, _lnx_safe_float(_lnx_dict(phase.get("totals")).get("absorb_weighted"), 0.0))
    other = max(0.0, weighted_total - absorb)
    return _lnx_pie_card(
        "化解占总贡献",
        [
            {"label": "化解贡献", "value": absorb, "color": LNX_PIE_COLORS[0]},
            {"label": "其他贡献", "chart_label": "其他贡献", "value": other, "color": LNX_PIE_OTHER_COLOR},
        ],
    )


def _lnx_wave_pills(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<div class=\"muted\">无波次数据</div>"
    total_cells = "\n".join(
        (
            "<div class=\"wave-card\">"
            f"<div class=\"wave-index\">W{row['index']} / {row['time_weight']:.2f}</div>"
            f"<div class=\"wave-value\">{_lnx_format_number(row['total_weighted'])}</div>"
            "</div>"
        )
        for row in rows
    )
    absorb_cells = "\n".join(
        (
            "<div class=\"wave-card\">"
            f"<div class=\"wave-index\">W{row['index']} / {row['time_weight']:.2f}</div>"
            f"<div class=\"wave-value\">{_lnx_format_number(row['absorb_weighted'])}</div>"
            "</div>"
        )
        for row in rows
    )
    return f"""
    <div class="wave-stack">
        <div class="wave-label-pill">总贡献</div>
        <div class="wave-grid">{total_cells}</div>
        <div class="wave-label-pill">化解</div>
        <div class="wave-grid">{absorb_cells}</div>
    </div>
    """


def render_lnx_analysis_html(raw_data: Any, anonymous: bool = False) -> str:
    phases = build_lnx_analysis_data(raw_data, anonymous)
    lnx_mark = ASSETS + "/image/jx3/calculator/lnx_mark.png"
    sections = []
    for phase in phases:
        combined_table = _lnx_table(
            ["#", "角色", "加权总贡献", "加权减伤", "加权治疗"],
            _lnx_contribution_rows(phase["players"][:10]),
            css_class="contribution-summary-table",
        )
        mitigation_table = _lnx_table(
            ["#", "角色", "加权减伤"],
            _lnx_single_contribution_rows(phase["mitigation_players"][:10], "mitigation_weighted"),
            css_class="contribution-side-table",
        )
        heal_table = _lnx_table(
            ["#", "角色", "加权治疗"],
            _lnx_single_contribution_rows(phase["heal_players"][:10], "heal_weighted"),
            css_class="contribution-side-table",
        )
        buff_table = _lnx_table(
            ["#", "来源", "Buff", "减伤", "加权贡献", "覆盖"],
            _lnx_buff_rows(phase["mitigation_buffs"]),
            css_class="buff-detail-table",
        )
        pie_panel = "\n".join(
            [
                _lnx_pie_html("减伤贡献占比 Top 5", phase["mitigation_players"], "mitigation_weighted"),
                _lnx_pie_html("治疗贡献占比 Top 5", phase["heal_players"], "heal_weighted"),
                _lnx_absorb_pie_html(phase),
            ]
        )
        section = f"""
        <section class="phase-card">
            <img class="phase-watermark" src="{html.escape(lnx_mark)}" aria-hidden="true">
            <div class="phase-header">
                <div>
                    <div class="phase-name">Phase {phase['phase_index']}</div>
                    <div class="phase-meta">波次 {phase['wave_count']} / 终止 W{phase['terminal_wave']} / trigger_line {html.escape(str(phase['trigger_line']))}</div>
                </div>
                <div class="badge">按 weighted_contribution 降序</div>
            </div>
            <div class="triple-col">
                <div>
                    <div class="section-title">综合贡献 Top 10</div>
                    {combined_table}
                </div>
                <div>
                    <div class="section-title">减伤贡献 Top 10</div>
                    {mitigation_table}
                </div>
                <div>
                    <div class="section-title">治疗贡献 Top 10</div>
                    {heal_table}
                </div>
            </div>
            <div class="detail-row">
                <div>
                    <div class="section-title">减伤 Buff 明细</div>
                    {buff_table}
                </div>
                <div>
                    <div class="section-title">贡献占比</div>
                    <div class="pie-panel">{pie_panel}</div>
                </div>
            </div>
            <div class="section-title">Wave 加权总贡献与化解总量</div>
            {_lnx_wave_pills(phase['waves'])}
        </section>
        """
        sections.append(section)
    if not sections:
        sections.append("<section class=\"phase-card\"><div class=\"phase-name\">未识别到鲁念雪分析数据</div></section>")
    return Template(lnx_template_body).render(
        font=ASSETS + "/font/PingFangSC-Semibold.otf",
        lnx_mark=lnx_mark,
        decay_rate=LNX_DECAY_RATE,
        sections="\n".join(sections),
        saohua=get_saohua(),
    )


async def render_lnx_analysis(raw_data: Any, anonymous: bool = False):
    html_content = render_lnx_analysis_html(raw_data, anonymous)
    return await generate(html_content, ".lnx-report", segment=True, viewport={"width": 1800, "height": 1200})


async def LNXAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(
            f"{Config.jx3.api.cqc_url}/lnx_analyze",
            json={"jcl_url": url, "jcl_name": file_name},
            timeout=600
        )
        data = resp.json()
    if isinstance(data, dict) and data.get("code") not in (None, 200):
        return data.get("msg") or "鲁念雪分析失败，请检查 JCL 是否完整。"
    raw_data = data.get("data", data) if isinstance(data, dict) else data
    return await render_lnx_analysis(raw_data, anonymous)

# A Shi Na (Cheng Qing)
async def ASNAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/asn_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()
    tables = []
    final_tables = []
    for each_record in data["data"]["hps"]:
        if each_record == {}:
            final_tables.append(
                Template(yxc_table).render(
                    tables = "\n".join(tables)
                )
            )
            tables = []
            continue
        player_name = each_record["name"]
        if anonymous:
            player_name = "匿名玩家"
        tables.append(
            Template(hps_detail_template_body_main).render(
                icon=Kungfu.with_internel_id(int(each_record["kungfu_id"]), True).icon,
                name=player_name,
                value=each_record["value"]
            )
        )
        skills = dict(sorted(each_record["skills"].items(), key=lambda item: sum(item[1]), reverse=True))
        for skill_name, skill_values in skills.items():
            tables.append(
                Template(hps_detail_template_body_sub).render(
                    name = skill_name,
                    count = len(skill_values),
                    value = sum(skill_values),
                    percent = str(round(sum(skill_values) / each_record["value"] * 100, 2)) + "%"
                )
            )
    html = Template(
        read(TEMPLATES + "/jx3/health_detail.html")
    ).render(
        font = ASSETS + "/font/PingFangSC-Semibold.otf",
        tables = "\n".join(final_tables),
        saohua = get_saohua(),
        function_name = "阿史那承庆 · 死侍期间治疗吸收盾 HPS 统计"
    )
    hps_image = await generate(html, ".container", segment=True)
    round_tables = []
    for each_record in data["data"]["hit"]:
        round_rows = []
        for player_name, values in dict(sorted(each_record.items(), key=lambda item: sum(item[1].values()), reverse=True)).items():
            if anonymous:
                player_name = "匿名玩家"
            round_rows.append(
                Template(asn_qte_template_body_main).render(
                    name=player_name,
                    good=values["good"],
                    bad=values["bad"]
                )
            )
        round_table = Template(asn_qte_table).render(
            tables="\n".join(round_rows)
        )
        round_tables.append(round_table)
    html = Template(
        read(TEMPLATES + "/jx3/health_detail.html")
    ).render(
        font=ASSETS + "/font/PingFangSC-Semibold.otf",
        tables="\n".join(round_tables),
        saohua=get_saohua(),
        function_name="阿史那承庆 · QTE 统计"
    )

    qte_image = await generate(html, ".container", segment=True)
    return hps_image + qte_image

# Tang Huai Ren
async def THRAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/thr_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()

    if data["code"] == 400:
        return "未识别到首领通关，请更换 JCL！"

    final_dps = []
    final_hps = []

    team_total_damage = sum(r["total_damage"] for r in data["data"][0].values())
    team_total_damage_per_second = "{:,}".format(int(team_total_damage / data["battle_time"]))

    for player_name, player_data in data["data"][0].items():
        if anonymous:
            player_name = "匿名玩家"
        kungfu: Kungfu = Kungfu.with_internel_id(int(player_data["kungfu_id"]))
        single_record = Template(bla_template_body).render(
            icon = kungfu.icon,
            name = player_name + " - " + str(round(player_data["total_damage"] / team_total_damage * 100, 2)) + "%",
            rdps = "{:,}".format(int(player_data["total_damage"])),
            display = str(round(player_data["total_damage"] / list(data["data"][0].values())[0]["total_damage"], 4) * 100),
            color = kungfu.color,
            percent = "{:,}".format(int(player_data['damage_per_second']))
        )
        final_dps.append(
            single_record
        )

    for player_name, player_data in data["data"][1].items():
        if anonymous:
            player_name = "匿名玩家"
        kungfu: Kungfu = Kungfu.with_internel_id(int(player_data["kungfu_id"]))
        final_hps.append(
            Template(bla_template_body.replace("dps-num", "hps-num")).render(
                icon = kungfu.icon,
                name = player_name,
                rdps = "{:,}".format(int(player_data["total_health"])),
                display = str(round(player_data["total_health"] / list(data["data"][1].values())[0]["total_health"] * 100, 2)),
                color = kungfu.color,
                percent = "{:,}".format(int(player_data['health_per_second']))
            )
        )
    try:
        save_data(data["data"][0], True, "THR")
        save_data(data["data"][1], False, "THR")
    except Exception:
        pass

    html = str(
        SimpleHTML(
            "jx3",
            "cqc_dps",
            title = "Inkar Suki 唐怀仁 P1 战斗统计",
            battle_time = str(data["battle_time"]) + f"s | 总 DPS：{team_total_damage_per_second}",
            dps_stastic = "\n".join(final_dps),
            hps_stastic = "\n".join(final_hps),
            saohua = get_saohua(),
            font = ASSETS + "/font/PingFangSC-Semibold.otf"
        )
    )
    dps_image = await generate(html, ".container", segment=True)
    return dps_image

# Tang Huai ren Final
async def THFAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(f"{Config.jx3.api.cqc_url}/thf_analyze", json={"jcl_url": url, "jcl_name": file_name}, timeout=600)
        data = resp.json()

    if data["code"] == 400:
        return "未识别到首领通关，请更换 JCL！"

    final_dps = []
    final_hps = []

    team_total_damage = sum(r["total_damage"] for r in data["data"][0].values())
    team_total_damage_per_second = "{:,}".format(int(team_total_damage / data["battle_time"]))

    for player_name, player_data in data["data"][0].items():
        if anonymous:
            player_name = "匿名玩家"
        kungfu: Kungfu = Kungfu.with_internel_id(int(player_data["kungfu_id"]))
        single_record = Template(bla_template_body).render(
            icon = kungfu.icon,
            name = player_name + " - " + str(round(player_data["total_damage"] / team_total_damage * 100, 2)) + "%",
            rdps = "{:,}".format(int(player_data["total_damage"])),
            display = str(round(player_data["total_damage"] / list(data["data"][0].values())[0]["total_damage"], 4) * 100),
            color = kungfu.color,
            percent = "{:,}".format(int(player_data['damage_per_second']))
        )
        final_dps.append(
            single_record
        )

    for player_name, player_data in data["data"][1].items():
        if anonymous:
            player_name = "匿名玩家"
        kungfu: Kungfu = Kungfu.with_internel_id(int(player_data["kungfu_id"]))
        final_hps.append(
            Template(bla_template_body.replace("dps-num", "hps-num")).render(
                icon = kungfu.icon,
                name = player_name,
                rdps = "{:,}".format(int(player_data["total_health"])),
                display = str(round(player_data["total_health"] / list(data["data"][1].values())[0]["total_health"] * 100, 2)),
                color = kungfu.color,
                percent = "{:,}".format(int(player_data['health_per_second']))
            )
        )

    html = str(
        SimpleHTML(
            "jx3",
            "cqc_dps",
            title = "Inkar Suki 唐怀仁 P3 战斗统计",
            battle_time = str(data["battle_time"]) + f"s | 总 DPS：{team_total_damage_per_second}",
            dps_stastic = "\n".join(final_dps),
            hps_stastic = "\n".join(final_hps),
            saohua = get_saohua(),
            font = ASSETS + "/font/PingFangSC-Semibold.otf"
        )
    )
    dps_image = await generate(html, ".container", segment=True)
    return dps_image

# Liu Gong Zi
async def LGZAnalyze(file_name: str, url: str, anonymous: bool = False, user_id: int = 0):
    async with AsyncClient(verify=False) as client:
        resp = await client.post(
            f"{Config.jx3.api.cqc_url}/lgz_analyze",
            json={
                "jcl_url": url,
                "jcl_name": file_name
            },
            timeout=600
        )
        data = resp.json()

    tables = []
    final_tables = []

    data = data["data"]

    if len(data) == 0:
        return "未识别到有效传功次数，请检查该 JCL 是否为 25人英雄阆风悬城 - 柳公子 的 JCL！"

    def flush_tables():
        nonlocal tables, final_tables
        if not tables:
            return
        final_tables.append(
            Template(lgz_table).render(
                tables="\n".join(tables)
            )
        )
        tables = []
    for each_record in data:
        if not each_record:
            flush_tables()
            continue
        if each_record.get("disarm_kungfu") is not None:
            tables.append(
                Template(lgz_detail_template_body_main).render(
                    icon=Kungfu.with_internel_id(
                        int(each_record["disarm_kungfu"]),
                        True
                    ).icon,
                    name=each_record["disarm_name"],
                    status="点名缴械",
                    status_icon=ASSETS + "/image/jx3/attributes/2399.png",
                    time=Time(each_record["disarm_time"]).format("%H:%M:%S")
                )
            )
        if each_record.get("placer_kungfu") is not None:
            tables.append(
                Template(lgz_detail_template_body_main).render(
                    icon=Kungfu.with_internel_id(
                        int(each_record["placer_kungfu"]),
                        True
                    ).icon,
                    name=each_record["placer_name"],
                    status="放置武器",
                    status_icon=ASSETS + "/image/jx3/attributes/4558.png",
                    time=Time(each_record["placer_time"]).format("%H:%M:%S")
                )
            )
        transferers = sort_dict_list(
            each_record.get("transferers", []),
            "transferer_time"
        )
        for each_transferer in transferers:
            tables.append(
                Template(lgz_detail_template_body_sub).render(
                    icon=Kungfu.with_internel_id(
                        int(each_transferer["transferer_kungfu"]),
                        True
                    ).icon,
                    name=each_transferer["transferer_name"],
                    status="传功完成",
                    status_icon=ASSETS + "/image/jx3/attributes/2401.png",
                    time=Time(each_transferer["transferer_time"]).format("%H:%M:%S")
                )
            )
    flush_tables()
    html = Template(
        read(TEMPLATES + "/jx3/health_detail.html")
    ).render(
        font=ASSETS + "/font/PingFangSC-Semibold.otf",
        tables="\n".join(final_tables),
        saohua=get_saohua(),
        function_name="柳公子 · 神秘装置记录"
    )
    image = await generate(html, ".container", segment=True)
    return image
