from __future__ import annotations

import html
from typing import Any


def _format_compact_number(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "0"
    if abs(number) >= 100000000:
        return f"{number / 100000000:.2f}亿"
    if abs(number) >= 10000:
        return f"{number / 10000:.1f}万"
    return f"{int(number):,}"


def _format_seconds(value: float) -> str:
    if abs(value - round(value)) < 0.05:
        return f"{int(round(value))}s"
    return f"{value:.1f}s"


def _smooth_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    if len(points) == 1:
        x, y = points[0]
        return f"M{x:.2f},{y:.2f}"
    path = [f"M{points[0][0]:.2f},{points[0][1]:.2f}"]
    for index in range(len(points) - 1):
        p0 = points[index - 1] if index > 0 else points[index]
        p1 = points[index]
        p2 = points[index + 1]
        p3 = points[index + 2] if index + 2 < len(points) else p2
        c1x = p1[0] + (p2[0] - p0[0]) / 6
        c1y = p1[1] + (p2[1] - p0[1]) / 6
        c2x = p2[0] - (p3[0] - p1[0]) / 6
        c2y = p2[1] - (p3[1] - p1[1]) / 6
        path.append(f"C{c1x:.2f},{c1y:.2f} {c2x:.2f},{c2y:.2f} {p2[0]:.2f},{p2[1]:.2f}")
    return " ".join(path)


def _series_points(
    series: dict[str, Any],
    key: str,
    width: int,
    height: int,
    max_value: float,
    max_second: float,
    source_key: str,
) -> list[tuple[float, float]]:
    bins = series.get("adjusted", {}).get(source_key) or []
    x_denominator = max(1, max_second)
    points = []
    for item in bins:
        second = float(item.get("second", 0) or 0)
        value = float(item.get(key, 0) or 0)
        x = second / x_denominator * width
        y = height - (value / max_value * height if max_value else 0)
        points.append((x, y))
    return points


def _peak_point(
    series: dict[str, Any],
    width: int,
    height: int,
    max_value: float,
    max_second: float,
    source_key: str,
) -> tuple[float, float, dict[str, Any]] | None:
    bins = series.get("adjusted", {}).get(source_key) or []
    if not bins:
        return None
    peak = max(bins, key=lambda item: int(item.get("damage_per_second_bin", 0) or 0))
    all_points = _series_points(series, "damage_per_second_bin", width, height, max_value, max_second, source_key)
    if not all_points:
        return None
    peak_index = bins.index(peak)
    x, y = all_points[peak_index]
    return x, y, peak


def _buff_overlays_svg(
    buff_overlays: list[dict[str, Any]],
    width: int,
    height: int,
    max_second: float,
) -> str:
    if not buff_overlays:
        return ""
    frames = []
    labels = []
    for overlay in buff_overlays:
        try:
            start = max(0.0, float(overlay.get("start", 0) or 0))
            end = min(max_second, float(overlay.get("end", 0) or 0))
        except (TypeError, ValueError):
            continue
        if end <= start:
            continue
        row = max(0, int(overlay.get("row", 0) or 0))
        color = html.escape(str(overlay.get("color") or "#64748B"))
        label = html.escape(str(overlay.get("label") or ""))
        x = start / max_second * width
        frame_width = max(1, (end - start) / max_second * width)
        frames.append(
            f'<rect x="{x:.2f}" y="0" width="{frame_width:.2f}" height="{height}" '
            f'rx="4" fill="{color}" stroke="{color}" class="buff-frame"/>'
        )
        if label:
            label_x = x + 6
            anchor = "start"
            if label_x > width - 90:
                label_x = width - 6
                anchor = "end"
            label_y = min(height - 8, 18 + row * 18)
            labels.append(
                f'<text x="{label_x:.2f}" y="{label_y:.2f}" text-anchor="{anchor}" '
                f'class="buff-frame-label" fill="{color}">{label}</text>'
            )
    return "".join(frames + labels)


def _chart_svg(
    series_list: list[dict[str, Any]],
    key: str,
    colors: list[str],
    title: str,
    width: int,
    height: int,
    mark_peak: bool = False,
    source_key: str = "bins",
    buff_overlays: list[dict[str, Any]] | None = None,
    stroke_width: float = 4,
) -> str:
    max_value = max(
        (
            float(item.get(key, 0) or 0)
            for series in series_list
            for item in (series.get("adjusted", {}).get(source_key) or [])
        ),
        default=1,
    )
    max_value = max(max_value, 1)
    max_bin_second = max(
        (
            float(item.get("second", 0) or 0)
            for series in series_list
            for item in (series.get("adjusted", {}).get(source_key) or [])
        ),
        default=0,
    )
    terminal_second = max(
        (float((series.get("adjusted") or {}).get("battle_time", 0) or 0) for series in series_list),
        default=0,
    )
    terminal_tick_second = max(1, max_bin_second, terminal_second)
    max_second = terminal_tick_second + max(5, terminal_tick_second * 0.04)
    grid_lines = []
    for ratio in [0, 0.25, 0.5, 0.75, 1]:
        y = height - ratio * height
        value = max_value * ratio
        grid_lines.append(
            f'<line x1="0" y1="{y:.2f}" x2="{width}" y2="{y:.2f}" stroke="#e6e8ee" stroke-width="1"/>'
            f'<text x="-12" y="{y + 4:.2f}" text-anchor="end" class="axis-label">{html.escape(_format_compact_number(value))}</text>'
        )
    time_ticks = []
    tick = 0
    while tick < terminal_tick_second:
        time_ticks.append(float(tick))
        tick += 15
    terminal_tick_x = terminal_tick_second / max_second * width
    time_ticks = [
        tick_second
        for tick_second in time_ticks
        if abs(tick_second / max_second * width - terminal_tick_x) >= 48
    ]
    if not any(abs(t - terminal_tick_second) < 0.05 for t in time_ticks):
        time_ticks.append(terminal_tick_second)
    axis_ticks = []
    for tick_second in time_ticks:
        x = tick_second / max_second * width
        anchor = "middle"
        if x < 12:
            anchor = "start"
        elif x > width - 12:
            anchor = "end"
        axis_ticks.append(
            f'<line x1="{x:.2f}" y1="{height}" x2="{x:.2f}" y2="{height + 7}" stroke="#b7bcc8" stroke-width="1"/>'
            f'<text x="{x:.2f}" y="{height + 24}" text-anchor="{anchor}" class="axis-label">{html.escape(_format_seconds(tick_second))}</text>'
        )
    overlay_bands = _buff_overlays_svg(buff_overlays or [], width, height, max_second)
    paths = []
    peaks = []
    for index, series in enumerate(series_list):
        color = colors[index % len(colors)]
        points = _series_points(series, key, width, height, max_value, max_second, source_key)
        path = _smooth_path(points)
        paths.append(
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{stroke_width:g}" stroke-linecap="round"/>'
        )
        if mark_peak:
            peak = _peak_point(series, width, height, max_value, max_second, source_key)
            if peak is not None:
                x, y, item = peak
                peaks.append(
                    f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="{color}" stroke="#fff" stroke-width="2"/>'
                    f'<text x="{min(width - 8, x + 10):.2f}" y="{max(16, y - 10):.2f}" class="peak-label" fill="{color}">'
                    f'{html.escape(series.get("label", ""))}峰值 {_format_compact_number(item.get("damage_per_second_bin"))}</text>'
                )
    return (
        f'<div class="chart-title">{html.escape(title)}</div>'
        f'<svg viewBox="-78 -10 {width + 96} {height + 40}" class="chart">'
        + "".join(grid_lines)
        + overlay_bands
        + "".join(paths)
        + "".join(peaks)
        + f'<line x1="0" y1="{height}" x2="{width}" y2="{height}" stroke="#b7bcc8" stroke-width="1.5"/>'
        + "".join(axis_ticks)
        + '</svg>'
    )
