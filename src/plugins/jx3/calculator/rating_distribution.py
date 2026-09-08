from __future__ import annotations

import asyncio
from colorsys import hls_to_rgb
from functools import lru_cache
from hashlib import sha256
import json
from math import ceil, exp, floor, log10, sqrt
from pathlib import Path
import re
from typing import Any

from jinja2 import Environment

from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from src.const.jx3.kungfu import Kungfu
from src.utils.database import rank_db
from src.utils.database.classes import EquipmentRatingDpsRank
from src.utils.generate import generate
from src.utils.permission import check_permission, denied
from src.utils.time import Time

from .equipment_rating import (
    RATING_LOOP_LIST_KEYWORDS,
    _equipment_rating_rank_jcl_key,
    _fetch_equipment_rating_loop_entries,
    _fetch_supported_equipment_rating_data,
    _find_supported_kungfu,
)
from .universe import UniversalCalculator


RATING_DISTRIBUTION_PERMISSION = "jx3.calculator.rating.distribution.export"
RATING_DISTRIBUTION_USAGE = (
    "评级分布 <心法>：同图展示所有默认武器路由\n"
    "评级分布 <心法> <紫武/橙武/特效武器名称>：高亮指定路由，其余置灰\n"
    "评级分布 <心法> 评级列表\n"
    "例如：评级分布 剑纯\n"
    "例如：评级分布 剑纯 紫武\n"
    "例如：评级分布 太玄经 蛰灵\n"
    "奶妈：评级分布 <心法>（承压分布）\n"
    "各路由分别统计榜单内角色的最新有效记录，仅输出分布统计图。"
)


_SRC = Path(__file__).resolve().parents[3]
_PLOT_LEFT = 72
_PLOT_TOP = 34
_PLOT_WIDTH = 836
_PLOT_HEIGHT = 286
_GRID_POINTS = 321
_QUANTILES = (
    (0.25, "P25", "25% 分位", "#9a73b7"),
    (0.50, "P50", "中位数", "#b1683c"),
    (0.75, "P75", "75% 分位", "#578b80"),
)


@lru_cache(maxsize=1)
def _template():
    source = (_SRC / "templates" / "jx3" / "rating_distribution.html").read_text(
        encoding="utf-8"
    )
    return Environment(autoescape=True).from_string(source)


@lru_cache(maxsize=1)
def _appearance_assets() -> tuple[dict, dict[str, str], str]:
    """Reuse rating-card assets without importing the bot or resolving user paths."""
    assets = _SRC / "assets"
    try:
        colors = json.loads(
            (assets / "source" / "jx3" / "kungfu_colors.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        colors = {}
    icons = {
        path.stem: path.as_uri()
        for path in (assets / "image" / "jx3" / "kungfu").glob("*.png")
        if path.is_file()
    }
    avatar = assets / "image" / "jx3" / "equipment_rating" / "Inkar.jpg"
    return colors if isinstance(colors, dict) else {}, icons, avatar.as_uri() if avatar.is_file() else ""


def _appearance(kungfu_name: str) -> dict[str, str]:
    colors, icons, avatar = _appearance_assets()
    color_name = "问水诀" if kungfu_name == "山居问水剑·悟" else kungfu_name.removesuffix("·悟")
    color = colors.get(color_name, "#4f6f87")
    if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        color = "#4f6f87"
    rgb = tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))
    ink = rgb
    while True:
        channels = [channel / 255 for channel in ink]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
        luminance = sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
        if 1.05 / (luminance + 0.05) >= 4.5:
            break
        ink = tuple(int(channel * 0.92) for channel in ink)
    return {
        "theme_color": color,
        "theme_rgb": ", ".join(str(channel) for channel in rgb),
        "theme_ink": "#{:02x}{:02x}{:02x}".format(*ink),
        "kungfu_icon": icons.get(kungfu_name, ""),
        "header_avatar": avatar,
    }


def _quantile(values: list[int], probability: float) -> float:
    """Use inclusive linear interpolation between adjacent sorted records."""
    position = (len(values) - 1) * probability
    lower = floor(position)
    fraction = position - lower
    return values[lower] + (values[min(lower + 1, len(values) - 1)] - values[lower]) * fraction


def _number(value: float | int) -> str:
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def _axis_number(value: float | int) -> str:
    if abs(value) >= 100_000_000:
        return f"{value / 100_000_000:.2f}".rstrip("0").rstrip(".") + "亿"
    if abs(value) >= 10_000:
        return f"{value / 10_000:.2f}".rstrip("0").rstrip(".") + "万"
    return _number(value)


def _nice_step(value: float) -> float:
    power = 10 ** floor(log10(max(1e-300, value)))
    return next(multiplier * power for multiplier in (1, 2, 5, 10) if multiplier * power >= value)


def _route_color(weapon: str) -> str:
    """Keep weapon colors stable across requests and highlight selections."""
    fixed = {"紫武": "#9470c4", "橙武": "#df923d", "蛰灵": "#269b9f", "承压": "#528ebd"}
    if weapon in fixed:
        return fixed[weapon]
    hue = (184 + int.from_bytes(sha256(weapon.encode("utf-8")).digest()[:2], "big") % 4400 / 100) / 360
    channels = hls_to_rgb(hue, 0.46, 0.55)
    return "#{:02x}{:02x}{:02x}".format(*(round(channel * 255) for channel in channels))


def _bandwidth(values: list[int]) -> float:
    if len(values) < 2 or values[0] == values[-1]:
        return 0.0
    mean = sum(values) / len(values)
    deviation = sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))
    spread = (_quantile(values, 0.75) - _quantile(values, 0.25)) / 1.34
    scale = min(deviation, spread) if spread > 0 else deviation
    return max(1.0, 0.9 * scale * len(values) ** -0.2)


def _density(values: list[int], xs: list[float], bandwidth: float) -> list[float]:
    """Linear-bin samples before Gaussian smoothing: O(N + grid_size ** 2).

    The shared grid uses physical DPS/capacity units. Each route integrates to
    one independently, so sample count does not determine its curve height.
    """
    dx = xs[1] - xs[0]
    counts = [0.0] * len(xs)
    for value in values:
        position = max(0.0, min(len(xs) - 1.0, (value - xs[0]) / dx))
        index = min(len(xs) - 2, floor(position))
        fraction = position - index
        counts[index] += 1 - fraction
        counts[index + 1] += fraction
    # Sub-pixel peaks remain legible on a chart shared by distant routes.
    bandwidth = max(bandwidth, 1.5 * dx)
    radius = min(len(xs) - 1, ceil(4 * bandwidth / dx))
    kernel = [exp(-0.5 * (offset * dx / bandwidth) ** 2) for offset in range(radius + 1)]
    result = [0.0] * len(xs)
    for index, count in enumerate(counts):
        if count:
            for target in range(max(0, index - radius), min(len(xs), index + radius + 1)):
                result[target] += count * kernel[abs(target - index)]
    area = (sum(result) - (result[0] + result[-1]) / 2) * dx
    return [value / area for value in result]


def _chart_data(series: list[dict], highlighted_key: str | None) -> dict:
    """Prepare common axes before applying presentation-only highlighting."""
    populated = [item for item in series if item["values"]]
    minimum = min(item["values"][0] for item in populated)
    maximum = max(item["values"][-1] for item in populated)
    bandwidths = {item["key"]: _bandwidth(item["values"]) for item in populated}
    padding = max(max(bandwidths.values()) * 4, (maximum - minimum) * 0.05, 1)
    if minimum == maximum:
        padding = max(1, maximum * 0.02)
    axis_minimum = max(0, minimum - padding)
    axis_maximum = maximum + padding
    axis_span = axis_maximum - axis_minimum
    xs = [axis_minimum + axis_span * index / (_GRID_POINTS - 1) for index in range(_GRID_POINTS)]
    curves = {}
    for item in populated:
        if item["values"][0] != item["values"][-1]:
            curves[item["key"]] = _density(item["values"], xs, bandwidths[item["key"]])
    peak = max((max(curve) for curve in curves.values()), default=0)
    y_step = _nice_step(peak * 1.08 / 4) if peak else 1
    y_maximum = ceil(peak * 1.08 / y_step) * y_step if peak else 1
    exponent = floor(log10(y_maximum)) if peak else 0
    superscript = str(exponent).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))

    def x_position(value: float) -> float:
        return round(_PLOT_LEFT + (value - axis_minimum) / axis_span * _PLOT_WIDTH, 3)

    y_ticks = [
        {
            "y": round(_PLOT_TOP + _PLOT_HEIGHT - index * y_step / y_maximum * _PLOT_HEIGHT, 3),
            "label": _number(index * y_step / 10 ** exponent) if peak else "",
        }
        for index in range(round(y_maximum / y_step) + 1)
    ]
    x_step = max(1, _nice_step(axis_span / 6))
    x_ticks = []
    tick = ceil(axis_minimum / x_step) * x_step
    while tick <= axis_maximum:
        x_ticks.append({"x": x_position(tick), "label": _axis_number(tick), "value": tick})
        tick += x_step
    if len({tick["label"] for tick in x_ticks}) < len(x_ticks):
        for tick in x_ticks:
            tick["label"] = _number(tick["value"])

    rendered = []
    for index, item in enumerate(series):
        values = item["values"]
        muted = highlighted_key is not None and item["key"] != highlighted_key
        route = {
            **item,
            "count": _number(len(values)),
            "maximum": _number(values[-1]) if values else "—",
            "color": _route_color(item["weapon"]),
            "muted": muted,
            "selected": item["key"] == highlighted_key,
            "stroke": "#8aa0b3" if muted else _route_color(item["weapon"]),
            "opacity": 0.32 if muted else 1,
            "stroke_width": 1.6 if muted else 3,
            "quantiles": [
                {"key": key, "label": label, "color": color, "value": _number(_quantile(values, probability)) if values else "—"}
                for probability, key, label, color in _QUANTILES
            ],
            "path": "",
            "point_x": None,
            "note": "暂无数据" if not values else "",
        }
        if values:
            if values[0] == values[-1]:
                route["point_x"] = x_position(values[0])
                route["point_y"] = _PLOT_TOP + 24 + index % 4 * 18
                route["note"] = "单条记录 · 竖线示位置" if len(values) == 1 else "数值相同 · 竖线示位置"
            else:
                route["path"] = " ".join(
                    f"{'M' if index == 0 else 'L'}{x_position(value):.3f},{_PLOT_TOP + _PLOT_HEIGHT - density / y_maximum * _PLOT_HEIGHT:.3f}"
                    for index, (value, density) in enumerate(zip(xs, curves[item["key"]]))
                )
                if len(values) < 10:
                    route["note"] = "样本较少"
        rendered.append(route)
    return {
        "routes": rendered,
        "draw_routes": sorted(rendered, key=lambda item: not item["muted"]),
        "x_ticks": x_ticks,
        "y_ticks": y_ticks,
        "density_unit": f"×10{superscript}" if peak and exponent else "",
        "has_density": bool(peak),
        "minimum": _number(minimum),
        "maximum": _number(maximum),
    }


def build_distribution_html(
    series: list[dict],
    *,
    kungfu_name: str,
    metric_label: str,
    updated_at: str,
    highlighted_key: str | None = None,
) -> str:
    """Render independent exact-route samples, sharing one physical value axis.

    Each series supplies key, name, weapon and positive-integer values. Empty
    routes remain in the legend; an entirely empty selection is an error.
    """
    if not series or any(
        not isinstance(item, dict)
        or any(not isinstance(item.get(key), str) or not item[key] for key in ("key", "name", "weapon"))
        or not isinstance(item.get("values"), list)
        or any(type(value) is not int or value <= 0 for value in item["values"])
        for item in series
    ):
        raise ValueError("评级分布需要完整的路由信息与有效的正整数排名记录。")
    if not any(item["values"] for item in series):
        raise ValueError("评级分布暂无有效排名数据。")
    if len({item["key"] for item in series}) != len(series):
        raise ValueError("评级分布不能包含重复榜单。")
    if highlighted_key is not None and highlighted_key not in {item["key"] for item in series}:
        raise ValueError("评级分布的高亮榜单不在当前路由中。")
    ordered = [{**item, "values": sorted(item["values"])} for item in series]
    chart = _chart_data(ordered, highlighted_key)
    selected = next((item for item in chart["routes"] if item["selected"]), None)
    stats_values = selected["values"] if selected else []
    return _template().render(
        font=(_SRC / "assets" / "font" / "PingFangSC-Semibold.otf").as_uri(),
        kungfu_name=kungfu_name,
        route_name=selected["name"] if selected else ordered[0]["name"] if len(ordered) == 1 else "全部武器路由 · 同图对照",
        metric_label=metric_label,
        updated_at=updated_at,
        selected=selected,
        route_count=len(ordered),
        populated_count=sum(bool(item["values"]) for item in ordered),
        selected_minimum=_number(stats_values[0]) if stats_values else "—",
        selected_maximum=_number(stats_values[-1]) if stats_values else "—",
        **_appearance(kungfu_name),
        **chart,
    )


def _weapon_type(value: str) -> str:
    for name in ("紫武", "橙武"):
        if name in value:
            return name
    return value.strip()


def _jcl_route(jcl: dict[str, Any], source: str, user_id: int = 0) -> dict[str, str]:
    weapon = str(jcl.get("weapon") or "").strip()
    haste = str(jcl.get("haste") or "").strip()
    loop = str(jcl.get("loop") or "").strip()
    if not weapon or not haste or not loop:
        raise ValueError("评级循环数据不完整。")
    meta = {
        "jcl": {"weapon": weapon, "haste": haste, "raw_loop": loop},
        "jcl_source": source,
        "jcl_loop": {"user_id": user_id},
    }
    source_name = {"rating_jcl": "默认评级", "jcl": "公有循环", "custom_jcl": "自定义循环"}[source]
    return {
        "key": _equipment_rating_rank_jcl_key(meta),
        "name": f"{source_name} · {weapon}·{haste}_{loop}",
        "weapon": _weapon_type(weapon),
        "metric": "DPS",
    }


def _default_routes(item: dict[str, Any]) -> list[dict[str, str]]:
    if item.get("rating_model") == "therapy_ruin":
        model_name = str((item.get("jcl_record") or {}).get("season") or "").strip()
        if not model_name:
            raise ValueError("calculator 未提供奶妈承压模型信息。")
        return [{
            "key": _equipment_rating_rank_jcl_key({"rating_model": "therapy_ruin", "loop_name": model_name}),
            "name": f"承压模型 · 破产概率 {model_name}",
            "weapon": "承压",
            "metric": "承压值",
        }]
    # 与 calculator 的默认选择一致：每个武器类型取第一个评级专用 JCL。
    routes: dict[str, dict[str, str]] = {}
    for jcl in item.get("jcls") or []:
        route = _jcl_route(jcl, "rating_jcl")
        routes.setdefault(route["weapon"], route)
    return list(routes.values())


def _select_weapon_route(routes: list[dict[str, str]], selector: str) -> dict[str, str] | None:
    if selector in {"特效", "特效武器"}:
        matches = [route for route in routes if route["weapon"] not in {"紫武", "橙武", "承压"}]
        return matches[0] if len(matches) == 1 else None
    return next((route for route in routes if route["weapon"] == selector), None)


def _rank_values(kungfu_id: int, route: dict[str, str]) -> list[int]:
    records = rank_db.where_all(
        EquipmentRatingDpsRank(),
        "kungfu_id = ? AND jcl_key = ?",
        kungfu_id,
        route["key"],
        default=[],
    ) or []
    return [
        int(record.dps)
        for record in records
        if isinstance(record, EquipmentRatingDpsRank) and int(record.dps or 0) > 0
    ]


async def _ensure_permission(event: MessageEvent, matcher: Matcher) -> None:
    if not check_permission(event.user_id, RATING_DISTRIBUTION_PERMISSION):
        await matcher.finish(denied(RATING_DISTRIBUTION_PERMISSION))


async def _send_distribution(
    matcher: Matcher,
    kungfu_id: int,
    routes: list[dict[str, str]],
    *,
    highlighted_key: str | None = None,
) -> None:
    kungfu_name = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True).name or str(kungfu_id)
    if not routes:
        await matcher.finish(f"{kungfu_name}当前没有可用的评级路由。")
        return
    try:
        series = [{**route, "values": _rank_values(kungfu_id, route)} for route in routes]
    except Exception:
        logger.exception("评级分布排名记录读取失败")
        await matcher.finish("评级分布读取失败，请稍后重试。")
        return
    if not any(item["values"] for item in series):
        label = f"【{routes[0]['name']}】" if len(routes) == 1 else "各武器路由"
        await matcher.finish(f"{kungfu_name}{label}暂无有效排名数据。")
        return
    try:
        html_source = await asyncio.to_thread(
            build_distribution_html,
            series,
            kungfu_name=kungfu_name,
            metric_label=routes[0]["metric"],
            updated_at=Time().format(),
            highlighted_key=highlighted_key,
        )
        image = await generate(
            html_source,
            ".rating-distribution",
            segment=True,
            viewport={"width": 1220, "height": 1000},
        )
    except Exception:
        logger.exception("评级分布图片生成失败")
        await matcher.finish("评级分布图片生成失败，请稍后重试。")
        return
    try:
        await matcher.finish(image)
    except ActionFailed:
        await matcher.finish("评级分布图片已生成，但 QQ/NapCat 拒绝了图片上传，请稍后重试。")


async def _choose_routes(
    event: MessageEvent,
    matcher: Matcher,
    state: T_State,
    kungfu_id: int,
    routes: list[dict[str, str]],
) -> None:
    if not routes:
        await matcher.finish("该心法当前没有可用的评级循环。")
        return
    state["rating_distribution_user_id"] = event.user_id
    state["rating_distribution_kungfu_id"] = kungfu_id
    state["rating_distribution_routes"] = routes
    lines = ["请选择评级分布榜单，回复序号出图（回复“取消”退出）："]
    for index, route in enumerate(routes, 1):
        lines.append(f"{index}. {route['name']}")
    await matcher.send("\n".join(lines))


async def handle_rating_distribution(
    event: MessageEvent, matcher: Matcher, state: T_State, args: Message,
) -> None:
    await _ensure_permission(event, matcher)
    parts = args.extract_plain_text().split()
    if not parts or parts[0].lower() in {"help", "帮助", "?", "？"}:
        await matcher.finish(RATING_DISTRIBUTION_USAGE)
        return
    if len(parts) > 2:
        await matcher.finish("参数格式错误。\n" + RATING_DISTRIBUTION_USAGE)
        return
    raw_kungfu = Kungfu.with_internel_id(parts[0], convert_to_pc=True) if parts[0].isdigit() else Kungfu(parts[0])
    kungfu = Kungfu.with_internel_id(raw_kungfu.id or 0, convert_to_pc=True)
    if not kungfu.id:
        await matcher.finish("未识别该心法，请使用心法名称、简称或心法 ID。")
        return
    selector = parts[1] if len(parts) == 2 else ""
    try:
        supported = await _fetch_supported_equipment_rating_data()
        if isinstance(supported, str):
            await matcher.finish(supported)
            return
        item = _find_supported_kungfu(supported.get("kungfus") or [], kungfu.id)
        if item is None:
            await matcher.finish(f"当前装备评级暂不支持 {kungfu.name}。")
            return
        kungfu_id = int(item["kungfu_id"])
        routes = _default_routes(item)
    except (ValueError, TypeError, KeyError, AttributeError):
        logger.exception("评级分布循环信息读取失败")
        await matcher.finish("评级分布查询失败：calculator 返回的循环信息不完整，请检查或重启 calculator。")
        return

    if selector in RATING_LOOP_LIST_KEYWORDS and item.get("rating_model") != "therapy_ruin":
        try:
            entries = await _fetch_equipment_rating_loop_entries(event, UniversalCalculator(kungfu_id=kungfu_id))
            if not isinstance(entries, str):
                routes = [
                    _jcl_route(entry, "custom_jcl" if entry.get("user_id") else "jcl", int(entry.get("user_id") or 0))
                    for entry in entries
                ]
        except Exception:
            logger.exception("评级分布公有/自定义循环列表读取失败")
            await matcher.finish("评级分布循环列表查询失败，请检查 calculator 服务后重试。")
            return
        if isinstance(entries, str):
            await matcher.finish(entries or "该心法当前没有可用的评级循环。")
            return
        await _choose_routes(event, matcher, state, kungfu_id, routes)
        return

    if item.get("rating_model") == "therapy_ruin":
        if selector and selector not in RATING_LOOP_LIST_KEYWORDS | {"承压", "默认"}:
            await matcher.finish(f"{kungfu.name}使用承压模型，不区分武器循环。请发送：评级分布 {kungfu.name}")
            return
        await _send_distribution(matcher, kungfu_id, routes)
        return
    if not selector:
        await _send_distribution(matcher, kungfu_id, routes)
        return
    route = _select_weapon_route(routes, selector)
    if route is None:
        names = "、".join(route["weapon"] for route in routes) or "无"
        await matcher.finish(f"{kungfu.name}没有唯一匹配的【{selector}】评级路由。\n可用路由：{names}")
        return
    await _send_distribution(matcher, kungfu_id, routes, highlighted_key=route["key"])


async def handle_rating_distribution_order(
    event: MessageEvent, matcher: Matcher, state: T_State, order: Message,
) -> None:
    await _ensure_permission(event, matcher)
    routes = state.get("rating_distribution_routes")
    kungfu_id = state.get("rating_distribution_kungfu_id")
    if (
        state.get("rating_distribution_user_id") != event.user_id
        or not isinstance(routes, list)
        or not routes
        or not isinstance(kungfu_id, int)
    ):
        await matcher.finish("评级分布会话已失效，请重新发起命令。")
        return
    text = order.extract_plain_text().strip()
    if text in {"取消", "退出"}:
        await matcher.finish("已取消评级分布查询。")
        return
    if not text.isascii() or not text.isdigit() or not 1 <= int(text) <= len(routes):
        await matcher.reject(f"请输入 1～{len(routes)} 的序号，或回复“取消”。")
        return
    route = routes[int(text) - 1]
    await _send_distribution(matcher, kungfu_id, [route], highlighted_key=route["key"])
