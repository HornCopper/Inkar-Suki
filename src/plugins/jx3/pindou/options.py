from __future__ import annotations

from typing import Any


DEFAULT_OPTIONS: dict[str, Any] = {
    "width": 400,
    "budget": 30000,
    "mode": "economy",
    "orientation": "ground",
    "pixelSize": 0.5,
}

OPTION_ORDER = tuple(DEFAULT_OPTIONS)

PARAMETER_PROMPT = """请按顺序回复，用空格分隔：
宽度：4–400（整数）
家具上限：1–30000（整数）
模式：省家具 / 颜色还原
方向：平铺 / 竖立
单格边长：0.5–8米

默认：400 30000 省家具 平铺 0.5
只改宽度可回复：128
回复“默认”直接使用；“-”或末尾省略项用默认值。“取消”退出。"""


class PindouOptionError(ValueError):
    pass


def _integer(token: str, field: str, minimum: int, maximum: int) -> int:
    try:
        value = int(token)
    except ValueError as exc:
        raise PindouOptionError(f"{field} 必须是整数。") from exc
    if not minimum <= value <= maximum:
        raise PindouOptionError(f"{field} 必须在 {minimum}-{maximum} 之间。")
    return value


def _number(token: str, field: str, minimum: float, maximum: float) -> float | int:
    try:
        value = float(token)
    except ValueError as exc:
        raise PindouOptionError(f"{field} 必须是数字。") from exc
    if not minimum <= value <= maximum:
        raise PindouOptionError(f"{field} 必须在 {minimum:g}-{maximum:g} 之间。")
    return int(value) if value.is_integer() else value


def _choice(token: str, field: str, choices: dict[str, str]) -> str:
    value = token.strip()
    if value not in choices:
        raise PindouOptionError(f"{field} 只能是 {' / '.join(choices)}。")
    return choices[value]


def _parse_value(field: str, token: str) -> Any:
    if field == "width":
        return _integer(token, "宽度", 4, 400)
    if field == "budget":
        return _integer(token, "家具上限", 1, 30000)
    if field == "mode":
        return _choice(token, "转换模式", {"省家具": "economy", "颜色还原": "fidelity"})
    if field == "orientation":
        return _choice(token, "放置方向", {"平铺": "ground", "竖立": "wall"})
    if field == "pixelSize":
        return _number(token, "单格边长", 0.5, 8)
    raise PindouOptionError(f"不支持的参数：{field}。")


def parse_options(text: str) -> dict[str, Any]:
    normalized = text.strip()
    if normalized.lower() in {"默认", "default"}:
        return DEFAULT_OPTIONS.copy()
    if not normalized:
        raise PindouOptionError("没有收到参数。")

    tokens = normalized.split()
    if len(tokens) > len(OPTION_ORDER):
        raise PindouOptionError(
            f"最多需要 {len(OPTION_ORDER)} 项，目前收到 {len(tokens)} 项。"
        )

    options = DEFAULT_OPTIONS.copy()
    for index, token in enumerate(tokens):
        if token in {"-", "默认"}:
            continue
        field = OPTION_ORDER[index]
        options[field] = _parse_value(field, token)
    return options


