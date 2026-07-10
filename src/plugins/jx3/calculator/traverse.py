from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any, cast

from src.config import Config
from src.const.path import ASSETS, build_path
from src.utils.analyze import Locations
from src.utils.database import attribute_db
from src.utils.database.classes import EquipmentRatingCache
from src.utils.database.attributes import Equip, TabCache
from src.utils.generate import generate
from src.utils.network import Request
from src.utils.time import Time

from .compare import AttributesFull
from .base import normalize_calculator_jcl_data
from .universe import UniversalCalculator


RANK_ICON_FILES = {
    "ACE": "rank_ace.png",
    "S+": "rank_s_plus.png",
    "S": "rank_s.png",
    "A": "rank_a.png",
    "B": "rank_b.png",
    "C": "rank_c.png",
    "D": "rank_d.png",
}

CACHE_SCHEMA_VERSION = 7


def parse_loop_name(name: str) -> dict[str, str]:
    if "路" in name:
        weapon, haste_loop = name.split("路", 1)
        haste, loop = haste_loop.split("_", 1)
        return {"weapon": weapon, "haste": haste, "loop": loop}
    match = re.match(r"^(.+?)(\d+)_([^_].*)$", name)
    if match is None:
        raise ValueError(f"无法解析循环名称：{name}")
    weapon, haste, loop = match.groups()
    return {"weapon": weapon, "haste": haste, "loop": loop}


def equipment_hash(
    *,
    jcl_data: list[list],
    kungfu_id: int,
    loop_name: str,
    income_name: str,
    formation_name: str,
    user_id: int,
) -> str:
    raw = {
        "cache_schema_version": CACHE_SCHEMA_VERSION,
        "jcl_data": jcl_data,
        "kungfu_id": kungfu_id,
        "loop_name": loop_name,
        "income_name": income_name,
        "formation_name": formation_name,
        "user_id": user_id,
    }
    content = json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_rating_cache(equip_hash: str) -> EquipmentRatingCache | None:
    return cast(
        EquipmentRatingCache | None,
        attribute_db.where_one(
            EquipmentRatingCache(),
            "equip_hash = ?",
            equip_hash,
            default=None,
        ),
    )


def delete_rating_cache(global_role_id: int, kungfu_id: int) -> bool:
    cache = cast(
        EquipmentRatingCache | None,
        attribute_db.where_one(
            EquipmentRatingCache(),
            "global_role_id = ? AND kungfu_id = ?",
            global_role_id,
            kungfu_id,
            default=None,
        ),
    )
    if cache is None:
        return False
    attribute_db.delete(
        EquipmentRatingCache(),
        "global_role_id = ? AND kungfu_id = ?",
        global_role_id,
        kungfu_id,
    )
    return True


def save_rating_cache(
    *,
    equip_hash: str,
    global_role_id: int,
    role_name: str,
    server_name: str,
    kungfu_id: int,
    loop_name: str,
    income_name: str,
    formation_name: str,
    raw_equips_data: list,
    ratings: list[dict[str, Any]],
) -> EquipmentRatingCache:
    old_cache = cast(
        EquipmentRatingCache | None,
        attribute_db.where_one(
            EquipmentRatingCache(),
            "global_role_id = ? AND kungfu_id = ?",
            global_role_id,
            kungfu_id,
            default=None,
        ),
    )
    cache = old_cache or EquipmentRatingCache()
    cache.equip_hash = equip_hash
    cache.global_role_id = global_role_id
    cache.role_name = role_name
    cache.server_name = server_name
    cache.kungfu_id = kungfu_id
    cache.loop_name = loop_name
    cache.income_name = income_name
    cache.formation_name = formation_name
    cache.raw_equips_data = raw_equips_data
    cache.ratings = ratings
    cache.timestamp = Time().raw_time
    attribute_db.save(cache)
    return cache


def get_latest_rating_cache(jcl_data: list[list], kungfu_id: int) -> EquipmentRatingCache | None:
    candidates = cast(
        list[EquipmentRatingCache],
        attribute_db.where_all(
            EquipmentRatingCache(),
            "kungfu_id = ?",
            kungfu_id,
            default=[],
        ),
    )
    matches = [
        cache
        for cache in candidates
        if (
            isinstance(cache, EquipmentRatingCache)
            and cache.raw_equips_data == jcl_data
            and bool(cache.ratings)
        )
    ]
    if not matches:
        return None
    return max(matches, key=lambda cache: cache.timestamp)


async def calculate_with_optimized_equips(
    instance: UniversalCalculator,
    loop_arg: dict[str, str],
    user_id: int = 0,
    timeout: int = 300,
) -> dict[str, Any] | str:
    params: dict[str, Any] = {
        "full_income": instance.income_list + instance.formation_list,
        "kungfu_id": instance.kungfu_id,
        "jcl_data": normalize_calculator_jcl_data(instance.jcl_data or instance.equip_data.equip_lines),
        "optimize_equips": True,
        **loop_arg,
    }
    url_path = "calculator_raw"
    if user_id:
        url_path = "calculator_custom"
        params["user_id"] = user_id
    data = (
        await Request(f"{Config.jx3.api.calculator_url}/{url_path}", params=params).post(
            timeout=timeout
        )
    ).json()
    if data.get("code") == 404:
        return data.get("msg", "未找到可用的循环！")
    return data


def _as_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", ""))
        except ValueError:
            return None
    return None


def _find_dps(data: dict[str, Any]) -> float | None:
    for key in ("damage_per_second", "dps", "DPS", "rdps"):
        if key in data:
            return _as_number(data[key])
    return None


def _find_item_id(data: dict[str, Any]) -> int | None:
    for key in ("item_id", "itemId", "ID", "id", "equip_id", "equipId"):
        value = data.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    equip = data.get("equip")
    if isinstance(equip, dict):
        return _find_item_id(equip)
    return None


def _find_location(data: dict[str, Any]) -> int | None:
    for key in ("location", "location_code", "position", "slot", "subtype"):
        value = data.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        if isinstance(value, str) and value in Locations:
            return Locations.index(value)
    return None


def _find_name(data: dict[str, Any]) -> str:
    for key in ("name", "Name", "equip_name", "equipName"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    equip = data.get("equip")
    if isinstance(equip, dict):
        return _find_name(equip)
    return "未知装备"


def _find_attr(data: dict[str, Any]) -> str:
    magic_attrs = _parse_magic_attrs(data)
    if magic_attrs:
        return magic_attrs
    for key in ("attr", "attrs", "attribute", "equip_attr", "equipAttr"):
        value = data.get(key)
        if isinstance(value, str):
            return _format_attr_text(value)
        if isinstance(value, list):
            return _format_attr_text(value)
    equip = data.get("equip")
    if isinstance(equip, dict):
        return _find_attr(equip)
    return ""


def _full_attr_name(attr_key: Any) -> str:
    return AttributesFull.get(str(attr_key), "")


def _parse_magic_attrs(data: dict[str, Any]) -> str:
    attrs = []
    for index in range(1, 21):
        key = f"Magic{index}Key"
        if key not in data:
            break
        attr_name = _full_attr_name(data[key])
        if attr_name:
            attrs.append(attr_name)
    return " ".join(attrs)


def _lookup_equip_attr(item_id: int | None, location: int | None) -> str:
    if item_id is None or location is None:
        return ""
    try:
        equip_data = TabCache.get_equip(int(item_id), _equip_tab_key(int(location)))
        magic_start = 53 if _equip_tab_key(int(location)) == 3 else 52
        attrs = []
        for index in range(magic_start, 68):
            attrib_key = equip_data[index]
            if attrib_key == "":
                break
            modify_type, _, _ = TabCache.get_attrib(attrib_key)
            attr_name = _full_attr_name(modify_type)
            if attr_name:
                attrs.append(attr_name)
        return " ".join(attrs)
    except Exception:
        return ""


def _format_attr_text(value: Any) -> str:
    if isinstance(value, list):
        return " ".join([_full_attr_name(item) or str(item) for item in value if item and str(item) != "体质"])
    if isinstance(value, str):
        return " ".join([_full_attr_name(item) or item for item in value.split() if item != "体质"])
    return ""


def _rating_attr(data: dict[str, Any], fallback: Any = "") -> str:
    attr = _find_attr(data)
    if attr:
        return attr
    return _format_attr_text(fallback)


def _find_quality(data: dict[str, Any]) -> int:
    for key in ("quality", "Quality", "level", "Level", "equip_level", "equipLevel"):
        value = data.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    equip = data.get("equip")
    if isinstance(equip, dict):
        return _find_quality(equip)
    return 0


def _equip_tab_key(location: int) -> int:
    if location in [3, 4, 8, 10, 11, 12]:
        return 1
    if location in [5, 6, 7, 9]:
        return 2
    return 3


def _lookup_equip_quality(item_id: int | None, location: int | None) -> int:
    if item_id is None or location is None:
        return 0
    try:
        equip_data = TabCache.get_equip(int(item_id), _equip_tab_key(int(location)))
        return int(equip_data[12] if _equip_tab_key(int(location)) == 3 else equip_data[11])
    except Exception:
        return 0


def _lookup_equip_peerless(item_id: int | None, location: int | None) -> bool:
    if item_id is None or location is None:
        return False
    try:
        equip_data = TabCache.get_equip(int(item_id), _equip_tab_key(int(location)))
        return "atSkillEventHandler" in equip_data
    except Exception:
        return False


def _current_equip_details(current_jcl_data: list[list]) -> dict[int, dict[str, Any]]:
    details: dict[int, dict[str, Any]] = {}
    Equip.purge()
    for line in current_jcl_data:
        if len(line) <= 2:
            continue
        try:
            location = int(line[0])
            equip = Equip(line)
            equip._pre_parse()
            equip.parse()
            equip._post_parse()
            details[location] = {
                "item_id": int(line[2]),
                "name": equip.name,
                "quality": equip.quality,
                "attr": _lookup_equip_attr(int(line[2]), int(line[0])),
                "peerless": equip.peerless,
            }
        except Exception:
            details[int(line[0])] = {
                "item_id": int(line[2]),
                "name": "当前装备",
                "quality": _lookup_equip_quality(int(line[2]), int(line[0])),
                "attr": _lookup_equip_attr(int(line[2]), int(line[0])),
                "peerless": _lookup_equip_peerless(int(line[2]), int(line[0])),
            }
    return details


def _iter_candidate_groups(data: dict[str, Any]) -> list[dict[str, Any]]:
    for key in (
        "equip_optimization",
        "optimized_equips",
        "optimize_equips",
        "equip_optimizations",
        "equip_compare",
        "equip_comparisons",
        "equips",
    ):
        value = data.get(key)
        if isinstance(value, dict) and isinstance(value.get("slots"), dict):
            return [
                {"location": location, "candidates": candidates}
                for location, candidates in value["slots"].items()
            ]
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            groups = []
            for location, candidates in value.items():
                if isinstance(candidates, dict):
                    group = dict(candidates)
                    group.setdefault("location", location)
                    groups.append(group)
                else:
                    groups.append({"location": location, "candidates": candidates})
            return groups
    return []


def _extract_candidates(group: Any) -> tuple[int | None, list[dict[str, Any]]]:
    if isinstance(group, list):
        return None, [item for item in group if isinstance(item, dict)]
    if not isinstance(group, dict):
        return None, []
    location = _find_location(group)
    for key in ("candidates", "items", "equips", "results", "data", "compare"):
        value = group.get(key)
        if isinstance(value, list):
            return location, [item for item in value if isinstance(item, dict)]
    if _find_dps(group) is not None:
        return location, [group]
    return location, []


def _rating_summary(data: dict[str, Any]) -> dict[str, Any]:
    summary = data.get("summary")
    if not isinstance(summary, dict):
        return {}
    return {
        "total_score_text": str(
            summary.get(
                "display_total_score_text",
                f"{summary.get('display_total_score', 0):.1f}",
            )
        ),
        "grade": str(summary.get("grade", "D")),
        "current_dps_text": _format_dps(_as_number(summary.get("current_dps")) or 0),
        "metric_name": str(summary.get("metric_name") or "DPS"),
        "metric_unit": str(summary.get("metric_unit") or "DPS"),
        "rated_slots": summary.get("rated_slots", 0),
        "total_slots": summary.get("total_slots", 0),
    }


def build_equipment_ratings_from_api(data: dict[str, Any], current_jcl_data: list[list]) -> list[dict[str, Any]]:
    summary = _rating_summary(data)
    current_details = _current_equip_details(current_jcl_data)
    results = []
    for slot in data.get("slots", []):
        if not isinstance(slot, dict):
            continue
        rating = slot.get("rating")
        current = slot.get("current") or {}
        best = slot.get("best") or {}
        if not isinstance(rating, dict) or not isinstance(current, dict) or not isinstance(best, dict):
            continue
        try:
            location_code = int(slot.get("location_code", 99))
        except (TypeError, ValueError):
            location_code = 99
        current_dps = _as_number(rating.get("current_dps")) or _as_number(current.get("dps")) or 0
        best_dps = _as_number(best.get("dps")) or current_dps
        percent_to_best = rating.get("percent_to_best")
        if not isinstance(percent_to_best, (int, float)):
            percent_to_best = round(current_dps / best_dps * 100, 2) if best_dps else 0
        result = {
            "location": slot.get("location_name") or (Locations[location_code] if location_code < len(Locations) else str(location_code)),
            "location_code": location_code,
            "item_id": current_details.get(location_code, {}).get("item_id", current.get("item_id") or current.get("ui_id")),
            "name": current_details.get(location_code, {}).get("name", _find_name(current)),
            "quality": current_details.get(location_code, {}).get("quality", _find_quality(current)),
            "attr": _rating_attr(current, current_details.get(location_code, {}).get("attr", "")),
            "grade": str(rating.get("grade", "D")),
            "score": rating.get("display_score", rating.get("score", 0)),
            "rank": rating.get("rank", "-"),
            "total": rating.get("total", "-"),
            "dps": int(current_dps),
            "best_name": _find_name(best),
            "best_quality": _find_quality(best),
            "best_attr": _rating_attr(best),
            "best_dps": int(best_dps),
            "diff_to_best": int(current_dps - best_dps),
            "percent_to_best": percent_to_best,
            "inferred_current": False,
            "metric_name": summary.get("metric_name", "DPS"),
            "metric_unit": summary.get("metric_unit", "DPS"),
            "rating_summary": summary,
        }
        results.append(result)
    return sorted(results, key=lambda item: item["location_code"])


async def request_equipment_ratings(
    *,
    instance: UniversalCalculator,
    loop_code: dict[str, str],
    role_name: str,
    server_name: str,
    global_role_id: int,
    user_id: int = 0,
) -> list[dict[str, Any]] | str:
    payload = {
        "kungfu_id": instance.kungfu_id,
        "jcl_data": normalize_calculator_jcl_data(instance.jcl_data or instance.equip_data.equip_lines),
        "role": {
            "name": role_name,
            "server": server_name,
            "global_role_id": global_role_id,
        },
        "full_income": instance.income_list + instance.formation_list,
        "candidate_level": {
            "min": 32500,
            "max": 43000,
        },
        **loop_code,
    }
    if user_id:
        payload["user_id"] = user_id
    try:
        result = (
            await Request(f"{Config.jx3.api.calculator_url}/equipment_rating", params=payload).post(timeout=300)
        ).json()
    except Exception as e:
        return f"装备评级计算失败：{e}"
    if result.get("code") != 200:
        return result.get("msg", "装备评级计算失败。")
    ratings = build_equipment_ratings_from_api(result["data"], instance.jcl_data or instance.equip_data.equip_lines)
    if not ratings:
        return format_rating_summary(ratings, detailed=True)
    return ratings


def format_rating_summary(ratings: list[dict[str, Any]], *, detailed: bool = False) -> str:
    if not ratings:
        return "本次计算未返回可解析的同部位装备对比数据。"
    lines = ["装备评级："]
    for rating in ratings:
        metric_unit = rating.get("metric_unit") or "DPS"
        line = (
            f"{rating['location']}：{rating['grade']} "
            f"#{rating['rank']}/{rating['total']} "
            f"{rating['percent_to_best']}% | "
            f"距最优 {rating['diff_to_best']:+,} {metric_unit}"
        )
        if detailed:
            line += f"\n  当前：{rating['name']}（{rating['dps']:,} {metric_unit}）"
            line += f"\n  最优：{rating['best_name']}（{rating['best_dps']:,} {metric_unit}）"
        lines.append(line)
    return "\n".join(lines)


def _format_dps(value: int | float) -> str:
    return f"{int(value):,}"


def _format_diff(value: int | float) -> str:
    return f"{int(value):+,}"


def _format_equip_cell(name: Any, quality: Any, attr: Any) -> str:
    quality_value = 0
    if isinstance(quality, int):
        quality_value = quality
    elif isinstance(quality, str) and quality.isdigit():
        quality_value = int(quality)
    quality_text = f"<span class=\"quality\">{quality_value}</span>" if quality_value > 0 else ""
    attr_text = f"<div class=\"attr\">{html.escape(str(attr))}</div>" if attr else ""
    return (
        "<div class=\"equip-name\">"
        f"{quality_text}{html.escape(str(name))}"
        "</div>"
        f"{attr_text}"
    )


def _asset_uri(*parts: str) -> str:
    return Path(build_path(ASSETS, list(parts))).as_uri()


def _format_grade_mark(grade: str) -> str:
    grade_icon = _asset_uri("image", "jx3", "equipment_rating", RANK_ICON_FILES.get(grade, "rank_d.png"))
    return (
        "<div class=\"grade-stack\">"
        f"<img class=\"grade-icon\" src=\"{grade_icon}\" alt=\"{html.escape(grade)}\">"
        "</div>"
    )


async def render_rating_table_image(
    ratings: list[dict[str, Any]],
    *,
    title: str = "装备遍历评级",
    subtitle: str = "",
):
    if not ratings:
        return format_rating_summary(ratings)
    rows = []
    for rating in ratings:
        grade = str(rating["grade"])
        note = "当前装备未在候选列表中，已纳入最优解比较" if rating.get("inferred_current") else ""
        diff = int(rating["diff_to_best"])
        current_equip = _format_equip_cell(
            rating["name"],
            rating.get("quality", 0),
            rating.get("attr", ""),
        )
        best_equip = _format_equip_cell(
            rating["best_name"],
            rating.get("best_quality", 0),
            rating.get("best_attr", ""),
        )
        diff_text = "最佳" if diff == 0 else _format_diff(diff)
        diff_class = "best" if diff == 0 else ("plus" if diff > 0 else "minus")
        rows.append(
            "<tr>"
            f"<td class=\"slot\">{html.escape(str(rating['location']))}</td>"
            f"<td>{_format_grade_mark(grade)}</td>"
            f"<td class=\"rank\">#{rating['rank']} / {rating['total']}</td>"
            f"<td class=\"percent\">{rating.get('score', rating['percent_to_best'])}</td>"
            f"<td class=\"percent best-percent\">100%</td>"
            f"<td class=\"dps\">{_format_dps(rating['dps'])}</td>"
            f"<td class=\"equip\">{current_equip}</td>"
            f"<td class=\"dps\">{_format_dps(rating['best_dps'])}</td>"
            f"<td class=\"equip\">{best_equip}</td>"
            f"<td class=\"diff {diff_class}\">{diff_text}</td>"
            f"<td class=\"note\">{html.escape(note)}</td>"
            "</tr>"
        )
    subtitle_html = f"<div class=\"subtitle\">{html.escape(subtitle)}</div>" if subtitle else ""
    summary = ratings[0].get("rating_summary", {}) if ratings else {}
    total_score_text = html.escape(str(summary.get("total_score_text", "--")))
    total_grade = html.escape(str(summary.get("grade", "D")))
    current_dps_text = html.escape(str(summary.get("current_dps_text", "--")))
    metric_name = html.escape(str(summary.get("metric_name", "DPS")))
    metric_unit = html.escape(str(summary.get("metric_unit", "DPS")))
    rated_slots = html.escape(str(summary.get("rated_slots", 0)))
    total_slots = html.escape(str(summary.get("total_slots", 0)))
    source_note = f"评分由装备评级接口计算；最优解从候选装备与当前装备中共同取最高{metric_name}。"
    html_source = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
* {{
    box-sizing: border-box;
}}
body {{
    margin: 0;
    width: 1600px;
    background: #f5f6fa;
    color: #333;
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
}}
.container {{
    --theme-color: #3f7fbf;
    width: 1560px;
    margin: 20px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}}
.header {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
    padding: 24px;
    background: #fafafa;
    border-bottom: 1px solid #ddd;
}}
.title {{
    font-size: 32px;
    font-weight: 800;
    line-height: 1.2;
    color: var(--theme-color);
    border-left: 5px solid var(--theme-color);
    padding-left: 12px;
}}
.subtitle {{
    margin-top: 8px;
    font-size: 18px;
    color: #555;
    padding-left: 17px;
}}
.legend {{
    max-width: 560px;
    text-align: right;
    font-size: 17px;
    line-height: 1.55;
    color: #777;
}}
.rating-total {{
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
    margin-bottom: 8px;
}}
.rating-total img {{
    width: 58px;
    height: 58px;
    object-fit: contain;
}}
.total-score {{
    font-size: 28px;
    line-height: 1.1;
    font-weight: 800;
    color: var(--theme-color);
}}
.total-meta {{
    margin-top: 4px;
    font-size: 15px;
    color: #777;
}}
table {{
    width: calc(100% - 48px);
    margin: 24px;
    border-collapse: collapse;
    table-layout: fixed;
    overflow: hidden;
    border-radius: 8px;
    background: #fff;
    border: 1px solid #eee;
}}
thead {{
    background: var(--theme-color);
    color: #fff;
}}
th {{
    padding: 13px 12px;
    font-size: 16px;
    font-weight: 700;
    text-align: left;
    white-space: nowrap;
}}
td {{
    padding: 12px;
    font-size: 17px;
    line-height: 1.35;
    border-bottom: 1px solid #f0f0f0;
    vertical-align: middle;
}}
tbody tr:nth-child(even) {{
    background: #fafafa;
}}
tbody tr:last-child td {{
    border-bottom: 0;
}}
.slot {{
    font-weight: 800;
    color: var(--theme-color);
}}
.grade-stack {{
    position: relative;
    width: 64px;
    height: 64px;
    margin: 0 auto;
}}
.grade-icon {{
    position: absolute;
    top: 0;
    left: 0;
    width: 64px;
    height: 64px;
    object-fit: contain;
}}
.rank,
.percent,
.dps,
.diff {{
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
}}
.percent {{
    font-weight: 800;
    color: var(--theme-color);
}}
.dps {{
    color: #333;
}}
.equip {{
    word-break: break-all;
    color: #444;
}}
.equip-name {{
    display: flex;
    align-items: baseline;
    gap: 7px;
    font-weight: 800;
    color: #333;
}}
.quality {{
    display: inline-block;
    min-width: 48px;
    padding: 2px 6px;
    border-radius: 6px;
    background: #f0f0f0;
    color: var(--theme-color);
    font-size: 14px;
    line-height: 1.3;
    text-align: center;
}}
.attr {{
    margin-top: 5px;
    font-size: 14px;
    line-height: 1.35;
    color: #777;
}}
.diff {{
    font-weight: 800;
}}
.plus {{
    color: var(--theme-color);
}}
.best {{
    color: var(--theme-color);
}}
.minus {{
    color: #777;
}}
.note {{
    font-size: 14px;
    color: #777;
}}
.footer {{
    margin-top: 0;
    padding: 15px 24px;
    background: #f0f0f0;
    border-top: 1px solid #ddd;
    text-align: center;
    font-size: 16px;
    color: #777;
}}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div>
            <div class="title">{html.escape(title)}</div>
            {subtitle_html}
        </div>
        <div class="legend">
            <div class="rating-total">
                <img src="{_asset_uri("image", "jx3", "equipment_rating", RANK_ICON_FILES.get(str(summary.get("grade", "D")), "rank_d.png"))}" alt="{total_grade}">
                <div>
                    <div class="total-score">{total_score_text} 分</div>
                    <div class="total-meta">{metric_name} {current_dps_text} · 有效部位 {rated_slots}/{total_slots}</div>
                </div>
            </div>
            <div>{source_note}</div>
        </div>
    </div>
    <table>
        <thead>
            <tr>
                <th style="width: 72px;">部位</th>
                <th style="width: 86px;">评级</th>
                <th style="width: 92px;">排名</th>
                <th style="width: 90px;">评分</th>
                <th style="width: 90px;">最优强度</th>
                <th style="width: 122px;">当前{metric_unit}</th>
                <th>当前装备</th>
                <th style="width: 122px;">最优{metric_unit}</th>
                <th>最优装备</th>
                <th style="width: 116px;">差值</th>
                <th style="width: 172px;">备注</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    <div class="footer">单件评分、总评分和评级均来自装备评级接口。</div>
</div>
</body>
</html>
"""
    return await generate(
        html_source,
        ".container",
        segment=True,
        wait_for_network=True,
        viewport={"width": 1600, "height": 980},
    )
