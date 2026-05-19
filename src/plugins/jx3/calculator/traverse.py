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

from .universe import UniversalCalculator


GRADE_THRESHOLDS = (
    ("S", 1.0),
    ("A", 0.985),
    ("B", 0.970),
    ("C", 0.950),
)

CACHE_SCHEMA_VERSION = 6


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
        "jcl_data": instance.jcl_data or instance.equip_data.equip_lines,
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
    for key in ("attr", "attrs", "attribute", "equip_attr", "equipAttr"):
        value = data.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return " ".join([str(item) for item in value])
    equip = data.get("equip")
    if isinstance(equip, dict):
        return _find_attr(equip)
    return ""


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
                "attr": equip.attribute,
                "peerless": equip.peerless,
            }
        except Exception:
            details[int(line[0])] = {
                "item_id": int(line[2]),
                "name": "当前装备",
                "quality": _lookup_equip_quality(int(line[2]), int(line[0])),
                "attr": "",
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


def build_equipment_ratings(
    calculator_data: dict[str, Any],
    current_jcl_data: list[list],
) -> list[dict[str, Any]]:
    current_dps = _find_dps(calculator_data)
    current_details = _current_equip_details(current_jcl_data)
    current_equips = {
        int(line[0]): int(line[2])
        for line in current_jcl_data
        if len(line) > 2 and isinstance(line[0], int)
    }
    results: list[dict[str, Any]] = []
    for group in _iter_candidate_groups(calculator_data):
        location, candidates = _extract_candidates(group)
        if not candidates:
            continue
        if location is None:
            location = _find_location(candidates[0])
        if location is None or location not in current_equips:
            continue
        parsed_candidates = []
        for candidate in candidates:
            dps = _find_dps(candidate)
            if dps is None:
                continue
            item_id = _find_item_id(candidate)
            quality = _find_quality(candidate) or _lookup_equip_quality(item_id, location)
            parsed_candidates.append(
                {
                    "item_id": item_id,
                    "name": _find_name(candidate),
                    "quality": quality,
                    "attr": _find_attr(candidate),
                    "dps": dps,
                }
            )
        if not parsed_candidates:
            continue
        parsed_candidates.sort(key=lambda item: item["dps"], reverse=True)
        current_item_id = current_equips[location]
        inferred_current = False
        current = next(
            (
                item
                for item in parsed_candidates
                if item["item_id"] == current_item_id
            ),
            None,
        )
        current_detail = current_details.get(
            location,
            {
                "item_id": current_item_id,
                "name": "当前装备",
                "quality": _lookup_equip_quality(current_item_id, location),
                "attr": "",
            },
        )
        if current is not None:
            current.update(
                {
                    "name": current_detail["name"],
                    "quality": current_detail["quality"],
                    "attr": current_detail["attr"],
                    "peerless": current_detail.get("peerless", False),
                }
            )
        if current is None and current_dps is not None:
            current = {
                "item_id": current_item_id,
                "name": current_detail["name"],
                "quality": current_detail["quality"],
                "attr": current_detail["attr"],
                "peerless": current_detail.get("peerless", False),
                "dps": current_dps,
            }
            parsed_candidates.append(current)
            parsed_candidates.sort(key=lambda item: item["dps"], reverse=True)
            inferred_current = True
        if current is None:
            continue
        best = parsed_candidates[0]
        best_dps = best["dps"]
        ratio = current["dps"] / best_dps if best_dps else 0
        grade = "D"
        for level, threshold in GRADE_THRESHOLDS:
            if ratio >= threshold:
                grade = level
                break
        rank = parsed_candidates.index(current) + 1
        results.append(
            {
                "location": Locations[location] if location < len(Locations) else str(location),
                "location_code": location,
                "item_id": current_item_id,
                "name": current["name"],
                "quality": current.get("quality", 0),
                "attr": current.get("attr", ""),
                "peerless": current.get("peerless", False),
                "grade": grade,
                "rank": rank,
                "total": len(parsed_candidates),
                "dps": int(current["dps"]),
                "best_name": best["name"],
                "best_quality": best.get("quality", 0),
                "best_attr": best.get("attr", ""),
                "best_dps": int(best["dps"]),
                "diff_to_best": int(current["dps"] - best["dps"]),
                "percent_to_best": round(ratio * 100, 2),
                "inferred_current": inferred_current,
                "candidates": parsed_candidates,
            }
        )
    return sorted(results, key=lambda item: item["location_code"])


def format_rating_summary(ratings: list[dict[str, Any]], *, detailed: bool = False) -> str:
    if not ratings:
        return "本次计算未返回可解析的同部位装备对比数据。"
    lines = ["装备评级："]
    for rating in ratings:
        line = (
            f"{rating['location']}：{rating['grade']} "
            f"#{rating['rank']}/{rating['total']} "
            f"{rating['percent_to_best']}% | "
            f"距最优 {rating['diff_to_best']:+,} DPS"
        )
        if detailed:
            line += f"\n  当前：{rating['name']}（{rating['dps']:,}）"
            line += f"\n  最优：{rating['best_name']}（{rating['best_dps']:,}）"
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
    grade_icon = _asset_uri("image", "jx3", "rank", f"rank_{grade.lower()}.png")
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
            f"<td class=\"percent\">{rating['percent_to_best']}%</td>"
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
    source_note = "百分比表示当前装备相对同部位最优解的强度；最优解从候选装备与当前装备中共同取最高 DPS。"
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
        <div class="legend">{source_note}</div>
    </div>
    <table>
        <thead>
            <tr>
                <th style="width: 72px;">部位</th>
                <th style="width: 86px;">评级</th>
                <th style="width: 92px;">排名</th>
                <th style="width: 90px;">当前强度</th>
                <th style="width: 90px;">最优强度</th>
                <th style="width: 122px;">当前 DPS</th>
                <th>当前装备</th>
                <th style="width: 122px;">候选最优</th>
                <th>最优装备</th>
                <th style="width: 116px;">差值</th>
                <th style="width: 172px;">备注</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    <div class="footer">S = 100%，A >= 98.5%，B >= 97%，C >= 95%，其余为 D。</div>
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
