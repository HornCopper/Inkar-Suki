"""Validated personal accent colors for the shared report UI."""

import re


DEFAULT_UI_COLOR = "默认"
_COLOR_PATTERN = re.compile(r"#?([0-9a-fA-F]{6})\Z")
_EXCLUDED_REPORT_MARKERS = ("ui-color-exempt", "equipment-card", "rating-distribution")


def supports_ui_color(source: str) -> bool:
    """Only shared report layouts are recolored; specialty layouts opt out."""
    return "report-header" in source and not any(
        marker in source for marker in _EXCLUDED_REPORT_MARKERS
    )


def normalize_ui_color(value: str) -> str | None:
    """Return a safe CSS hex color, the default marker, or None if invalid."""
    if value == DEFAULT_UI_COLOR:
        return DEFAULT_UI_COLOR
    match = _COLOR_PATTERN.fullmatch(value.strip())
    return f"#{match.group(1).upper()}" if match else None


def _mix(color: str, base: str, base_weight: float) -> str:
    source = [int(color[index:index + 2], 16) for index in (1, 3, 5)]
    target = [int(base[index:index + 2], 16) for index in (1, 3, 5)]
    channels = [round(a * (1 - base_weight) + b * base_weight) for a, b in zip(source, target)]
    return "#" + "".join(f"{channel:02X}" for channel in channels)


def _linear_channel(channel: float) -> float:
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def build_ui_color_css(value: str) -> str:
    """Theme standard report chrome, keeping semantic and specialty colors intact."""
    color = normalize_ui_color(value)
    if not color or color == DEFAULT_UI_COLOR:
        return ""
    surface = _mix(color, "#FFFFFF", 0.94)
    border = _mix(color, "#D7E0E9", 0.76)
    title = _mix(color, "#182B40", 0.65)
    rgb = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    luminance = sum(
        weight * _linear_channel(channel)
        for weight, channel in zip((0.2126, 0.7152, 0.0722), rgb)
    )
    on_accent = "#000000" if luminance > 0.18 else "#FFFFFF"
    return f"""
html body {{
  --inkar-accent: {color};
  --inkar-accent-ink: {title};
  --inkar-accent-surface: {surface};
  --inkar-border: {border};
  --inkar-muted-surface: {surface};
  --inkar-on-accent: {on_accent};
  --inkar-theme-ink: {title};
}}
html body .report-header {{
  border-left: 4px solid {color} !important;
}}
html body .report-header .report-title {{ color: {title} !important; }}
"""
