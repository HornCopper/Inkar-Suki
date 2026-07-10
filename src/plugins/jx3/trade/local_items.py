from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from src.const.path import ASSETS, build_path
from src.utils.database.tabs import read_tab


ITEM_TABLE = Path(build_path(ASSETS, ["source", "jx3", "tabs", "Item.txt"]))
DETAIL_TABLES = (
    (7, Path(build_path(ASSETS, ["source", "jx3", "tabs", "Custom_Armor.tab"]))),
    (8, Path(build_path(ASSETS, ["source", "jx3", "tabs", "Custom_Trinket.tab"]))),
    (6, Path(build_path(ASSETS, ["source", "jx3", "tabs", "Custom_Weapon.tab"]))),
    (5, Path(build_path(ASSETS, ["source", "jx3", "tabs", "Other.tab"]))),
)

COMPARABLE_MAGIC_TYPES = {
    "atPhysicsAttackPowerBase",
    "atMagicAttackPowerBase",
    "atPhysicsCriticalStrike",
    "atAllTypeCriticalStrike",
    "atPhysicsCriticalDamagePowerBase",
    "atAllTypeCriticalDamagePowerBase",
    "atPhysicsOvercomeBase",
    "atMagicOvercome",
    "atSurplusValueBase",
    "atStrainBase",
}
TRADE_BIND_TYPES = (0, 1, 2, None)
SHILIAN_BIND_TYPE = 2


def _field(row: list[str], header: list[str], key: str, default: str = "") -> str:
    try:
        index = header.index(key)
    except ValueError:
        return default
    if index >= len(row):
        return default
    return row[index]


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value in ("", None):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _bind_type(value: str) -> int | None:
    if value == "":
        return None
    return _to_int(value)


def is_trade_bind_type(bind_type: int | None) -> bool:
    return bind_type in TRADE_BIND_TYPES


def is_shilian_bind_type(bind_type: int | None) -> bool:
    return bind_type == SHILIAN_BIND_TYPE


def _tab_rows(tab: list[list[str]]) -> tuple[list[str], list[list[str]]]:
    return tab[0], tab[1:]


def _trade_id_sort_key(value: str) -> tuple[int, int, str]:
    tab_type, _, source_id = value.partition("_")
    return _to_int(tab_type), _to_int(source_id), value


@lru_cache(maxsize=1)
def _load_attribs() -> dict[str, dict[str, str]]:
    header, rows = _tab_rows(read_tab(str(Path(build_path(ASSETS, ["source", "jx3", "tabs", "Attrib.tab"])))))
    return {
        _field(row, header, "ID"): {
            "ModifyType": _field(row, header, "ModifyType"),
            "Param1Min": _field(row, header, "Param1Min"),
            "Param1Max": _field(row, header, "Param1Max"),
        }
        for row in rows
        if _field(row, header, "ID")
    }


@lru_cache(maxsize=1)
def _load_skill_events() -> dict[str, str]:
    header, rows = _tab_rows(read_tab(str(Path(build_path(ASSETS, ["source", "jx3", "tabs", "Skillevent.txt"])))))
    return {
        _field(row, header, "ID"): _field(row, header, "Desc")
        for row in rows
        if _field(row, header, "ID")
    }


def _row_magic_keys(row: list[str], header: list[str]) -> list[str]:
    attribs = _load_attribs()
    keys = []
    for index in range(1, 17):
        magic_id = _field(row, header, f"Magic{index}Type")
        magic_key = attribs.get(magic_id, {}).get("ModifyType", "")
        if magic_key in COMPARABLE_MAGIC_TYPES:
            keys.append(magic_key)
    return keys


def _row_skill_event_nodes(row: list[str], header: list[str]) -> list[dict[str, str]]:
    attribs = _load_attribs()
    skill_events = _load_skill_events()
    nodes = []
    for index in range(1, 17):
        magic_id = _field(row, header, f"Magic{index}Type")
        attrib = attribs.get(magic_id, {})
        if attrib.get("ModifyType") != "atSkillEventHandler":
            continue
        skill_event_id = attrib.get("Param1Min") or attrib.get("Param1Max")
        desc = skill_events.get(skill_event_id, "")
        if not desc:
            continue
        nodes.append(
            {
                "key": "atSkillEventHandler",
                "label": desc,
                "color": "orange",
            }
        )
    return nodes


def _attribute_nodes(keys: list[str], special_nodes: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    nodes = [
        {
            "key": key,
            "label": key,
            "color": "green",
        }
        for key in keys
    ]
    nodes.extend(special_nodes or [])
    return nodes


def _detail_item(tab_type: int, header: list[str], row: list[str], base: dict[str, Any], magic_keys: list[str] | None = None) -> dict[str, Any]:
    source_id = _field(row, header, "ID")
    trade_id = f"{tab_type}_{source_id}"
    ui_id = _field(row, header, "UiID")
    return {
        "id": trade_id,
        "UiID": _to_int(ui_id),
        "SourceID": _to_int(source_id),
        "Name": base.get("Name") or _field(row, header, "Name"),
        "IconID": base.get("IconID", 1434),
        "Desc": base.get("Desc"),
        "Level": _field(row, header, "Level") or _field(row, header, "_LEVEL"),
        "Quality": _to_int(_field(row, header, "Quality")),
        "BindType": _bind_type(_field(row, header, "BindType")),
        "SubType": _to_int(_field(row, header, "SubType")),
        "attributes": _attribute_nodes(magic_keys or [], _row_skill_event_nodes(row, header)),
    }


@lru_cache(maxsize=1)
def _load_local_items() -> dict[str, dict[str, Any]]:
    item_header, item_rows = _tab_rows(read_tab(str(ITEM_TABLE)))
    item_by_id = {
        _field(row, item_header, "ItemID"): {
            "id": _field(row, item_header, "ItemID"),
            "IconID": _to_int(_field(row, item_header, "IconID"), 1434),
            "Name": _field(row, item_header, "Name"),
            "Desc": _field(row, item_header, "Desc") or None,
        }
        for row in item_rows
        if _field(row, item_header, "ItemID")
    }

    items: dict[str, dict[str, Any]] = {}
    for tab_type, table in DETAIL_TABLES:
        header, rows = _tab_rows(read_tab(str(table)))
        for row in rows:
            ui_id = _field(row, header, "UiID")
            source_id = _field(row, header, "ID")
            if not ui_id:
                continue
            base = item_by_id.get(ui_id)
            if base is None:
                continue
            item_name = base.get("Name")
            if not item_name:
                continue
            bind_type = _bind_type(_field(row, header, "BindType"))
            if not is_trade_bind_type(bind_type):
                continue

            trade_id = f"{tab_type}_{source_id}"
            current = items.get(trade_id)
            if current is None:
                items[trade_id] = _detail_item(tab_type, header, row, base)

    return items


def search_local_items(keyword: str, limit: int = 50) -> list[dict[str, Any]]:
    keyword = keyword.strip()
    if not keyword:
        return []

    items = _load_local_items()
    scored: list[tuple[int, int, str, dict[str, Any]]] = []
    for item_id, item in items.items():
        name = item["Name"]
        if keyword not in name:
            continue
        if keyword == name:
            score = 0
        elif name.startswith(keyword):
            score = 1
        else:
            score = 2
        scored.append((score, len(name), item_id, item))

    scored.sort(key=lambda data: (data[0], data[1], _trade_id_sort_key(data[2])))
    return [item.copy() for *_, item in scored[:limit]]


def search_local_shilian_equips(
    name_prefix: str,
    quality: int,
    attr_keys: list[str] | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    item_header, item_rows = _tab_rows(read_tab(str(ITEM_TABLE)))
    item_by_id = {
        _field(row, item_header, "ItemID"): {
            "IconID": _to_int(_field(row, item_header, "IconID"), 1434),
            "Name": _field(row, item_header, "Name"),
            "Desc": _field(row, item_header, "Desc") or None,
        }
        for row in item_rows
        if _field(row, item_header, "ItemID")
    }
    expected = set(attr_keys) if attr_keys is not None else None
    results = []
    for tab_type, table in DETAIL_TABLES:
        if tab_type == 5:
            continue
        header, rows = _tab_rows(read_tab(str(table)))
        for row in rows:
            if not _field(row, header, "Name").startswith(name_prefix):
                continue
            if _to_int(_field(row, header, "Level")) != quality:
                continue
            if not is_shilian_bind_type(_bind_type(_field(row, header, "BindType"))):
                continue
            magic_keys = _row_magic_keys(row, header)
            if expected is not None and set(magic_keys) != expected:
                continue
            base = item_by_id.get(_field(row, header, "UiID"))
            if base is None:
                continue
            results.append(_detail_item(tab_type, header, row, base, magic_keys))
            if len(results) >= limit:
                return results
    return results
