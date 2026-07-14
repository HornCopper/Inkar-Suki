from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import re

from src.const.path import ASSETS, build_path
from src.plugins.jx3.calculator.compare import AttributesFull
from src.utils.database.attributes import TabCache


BOSS_TAB_PATH = Path(build_path(ASSETS, ["source", "jx3", "tabs", "boss"]))
SUPPORTED_ITEM_TYPES = {5, 6, 7, 8}


@lru_cache(maxsize=16)
def get_lua_boss_items(map_id: int) -> dict[str, set[tuple[int, int]]]:
    path = BOSS_TAB_PATH / f"MapID{map_id}.lua"
    if not path.exists():
        return {}

    source = path.read_text(encoding="gb18030")
    result: dict[str, set[tuple[int, int]]] = defaultdict(set)
    for block in re.findall(r"\[\d+\]\s*=\s*\{(.*?)\n\s*\},", source, re.DOTALL):
        item_type_match = re.search(r"\[1\]\s*=\s*(\d+)", block)
        item_id_match = re.search(r"\[2\]\s*=\s*(\d+)", block)
        boss_name_match = re.search(r'\[4\]\s*=\s*"([^"]+)"', block)
        if item_type_match and item_id_match and boss_name_match:
            item_type = int(item_type_match.group(1))
            if item_type in SUPPORTED_ITEM_TYPES:
                result[boss_name_match.group(1)].add(
                    (item_type, int(item_id_match.group(1)))
                )
    return dict(result)


def _rows_by_id(table: list[list]) -> dict[int, dict[str, str]]:
    headers = table[0]
    return {
        int(row[0]): dict(zip(headers, row))
        for row in table[1:]
        if row and row[0].isdigit()
    }


@lru_cache(maxsize=1)
def _item_icons() -> dict[int, tuple[str, str]]:
    return {
        int(row[0]): (row[1] or "1434", row[5] if len(row) > 5 else "")
        for row in TabCache.Item[1:]
        if len(row) > 1 and row[0].isdigit()
    }


def _icon(ui_id: str, kind: str, sub_kind: str) -> dict[str, str]:
    icon_id, _ = _item_icons().get(int(ui_id or 0), ("1434", ""))
    return {
        "FileName": f"https://icon.jx3box.com/icon/{icon_id}.png",
        "Kind": kind,
        "SubKind": sub_kind,
    }


@lru_cache(maxsize=None)
def _resolve_magic_type(value: str) -> str:
    if not value.isdigit():
        return value
    try:
        return TabCache.get_attrib(int(value))[0]
    except Exception:
        return value


def _local_item(item_type: int, row: dict[str, str]) -> dict:
    name = row.get("Name", "")
    ui_id = row.get("UiID", "0")
    if item_type == 5:
        _, item_desc = _item_icons().get(int(ui_id or 0), ("1434", ""))
        return {
            "Name": name,
            "BelongSchool": "",
            "Color": row.get("Quality", "4") or "4",
            "Type": row.get("_CATEGORY", ""),
            "Desc": item_desc,
            "Icon": _icon(ui_id, "其他", row.get("_CATEGORY", "")),
        }

    kind = {6: "武器", 7: "防具", 8: "首饰"}[item_type]
    detail_type = row.get("DetailType", "")
    sub_kind = (
        detail_type
        if detail_type not in ("", "0")
        else row.get("SubType") or kind
    )
    magic_types = [
        row.get(f"Magic{i}Type", "")
        for i in range(1, 17)
        if row.get(f"Magic{i}Type", "") not in ("", "0", "atInvalid")
    ]
    resolved_magic_types = [_resolve_magic_type(value) for value in magic_types]
    def generated_magic(magic_type: str) -> str:
        label = AttributesFull.get(magic_type, "")
        return f"{label}提高" if label else ""

    return {
        "Name": name,
        "Color": row.get("Quality", "4") or "4",
        "BelongSchool": row.get("BelongSchool", ""),
        "SubType": row.get("SubType", ""),
        "IsEffectPendant": (
            item_type == 8
            and row.get("SubType") == "7"
            and row.get("SkillID", "") not in ("", "0")
        ),
        "Type": row.get("_CATEGORY", ""),
        "Desc": "",
        "Icon": _icon(ui_id, kind, sub_kind),
        "ModifyType": [
            {"Attrib": {"GeneratedMagic": generated_magic(magic_type)}}
            for magic_type in resolved_magic_types
        ],
    }


@lru_cache(maxsize=1)
def _local_rows() -> dict[tuple[int, int], dict[str, str]]:
    tables = {
        5: TabCache.Other,
        6: TabCache.Custom_Weapon,
        7: TabCache.Custom_Armor,
        8: TabCache.Custom_Trinket,
    }
    return {
        (item_type, item_id): row
        for item_type, table in tables.items()
        for item_id, row in _rows_by_id(table).items()
    }


def get_local_lua_boss_drops(map_id: int) -> dict[str, list[dict]]:
    """返回以 Lua 为准、完全通过共享 TAB 缓存解析的掉落池。"""
    lua_items = get_lua_boss_items(map_id)
    if not lua_items:
        return {}
    local_rows = _local_rows()
    return {
        boss_name: [
            _local_item(key[0], local_rows[key])
            for key in item_keys
            if key in local_rows
        ]
        for boss_name, item_keys in lua_items.items()
    }
