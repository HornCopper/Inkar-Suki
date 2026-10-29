from collections import defaultdict
from copy import deepcopy
from functools import lru_cache
from typing import Any, cast

from src.utils.jx3_attributes import AttributesFull
from src.utils.jx3_tables import TALENT_HISTORY_ROOT, integer, rows, source_path, table

import json
import re

DATA_VERSION = "1.6.0.10022"
DATA_SEASON = "暗影千机"
LEGACY_SHILIAN_LEVELS = {
    28000: 473,
    30200: 511,
    32500: 550,
    35300: 597,
    38100: 644,
    41400: 700,
}
ITEM_TABLES = {
    5: "Other",
    6: "Custom_Weapon",
    7: "Custom_Armor",
    8: "Custom_Trinket",
    10: "HomelandItem",
}
RECIPE_CATEGORIES = ("tailoring", "cooking", "medicine", "founding", "furniture")
SHOP_TABLES = {
    f"{name.lower()}.tab": f"shop/{name}.tab"
    for name in ("Foundry", "Furniture", "Medical", "Seasoning", "Tailoring")
}
# 客户端商店列表中的家具表文件名原本拼作 funiture。
SHOP_TABLES["funiture.tab"] = SHOP_TABLES["furniture.tab"]
_ITEM_COLUMNS = (
    "Name", "UiID", "IconID", "Quality", "Level", "BindType", "BelongSchool", "SubType", "_CATEGORY",
    "MaxStrengthLevel", "SkillID", *(f"Magic{index}Type" for index in range(1, 17)),
    *(f"DiamondAttributeID{index}" for index in range(1, 4))
)

def _item_table(item_type: int) -> dict[str, dict[str, str]]:
    return table(f"item/{ITEM_TABLES[item_type]}.tab", columns = _ITEM_COLUMNS)

def _item_ui() -> dict[str, dict[str, str]]:
    return table("item/Item.txt", "ItemID", ("Name", "IconID", "Desc"))

def _attribute(value: str) -> dict[str, Any]:
    attributes = table("item/Attrib.tab", columns = ("ModifyType", "Param1Min", "Param1Max"))
    attribute = attributes.get(value, {})
    key = attribute.get("ModifyType", value if not str(value).isdigit() else "")
    label = AttributesFull.get(key, "")
    minimum = attribute.get("Param1Min", "")
    maximum = attribute.get("Param1Max", "")
    amount = minimum if minimum == maximum or not maximum else f"{minimum}~{maximum}"
    return {
        "Desc": key,
        "Attrib": {
            "GeneratedMagic": f"{label}提高{amount}" if label else "",
        },
    }

@lru_cache(maxsize = 32768)
def _item(key: str) -> dict[str, Any] | None:
    if not re.fullmatch(r"\d+_\d+", key):
        return None
    type_text, item_id = key.split("_")
    item_type = int(type_text)
    if item_type not in ITEM_TABLES:
        return None
    row = _item_table(item_type).get(item_id)
    if row is None:
        return None
    display = _item_ui().get(row.get("UiID", ""), {})
    icon_id = display.get("IconID") or row.get("IconID") or "1434"
    icon = table("Icon.txt", columns = ("Kind", "SubKind")).get(icon_id, {})
    result: dict[str, Any] = {
        "id": key,
        "Name": display.get("Name") or row["Name"],
        "IconID": integer(icon_id, 1434),
        "Desc": display.get("Desc", ""),
        "Color": integer(row.get("Quality"), 4),
        "Quality": integer(row.get("Level")),
        "Level": integer(row.get("Level")),
        "BindType": integer(row.get("BindType")),
        "BelongSchool": row.get("BelongSchool", ""),
        "SubType": row.get("SubType", ""),
        "Icon": {
            "FileName": f"https://icon.jx3box.com/icon/{icon_id}.png",
            "Kind": icon.get("Kind", ""),
            "SubKind": icon.get("SubKind", "其他"),
        },
    }
    if item_type in (6, 7, 8):
        result["ModifyType"] = [
            _attribute(row[f"Magic{index}Type"]) for index in range(1, 17)
            if row.get(f"Magic{index}Type") not in (None, "", "0", "atInvalid")
        ]
        result["DiamonAttribute"] = [
            _attribute(row[f"DiamondAttributeID{index}"]) for index in range(1, 4)
            if row.get(f"DiamondAttributeID{index}") not in (None, "", "0")
        ]
        result["MaxStrengthLevel"] = integer(row.get("MaxStrengthLevel"))
        result["IsEffectPendant"] = (
            item_type == 8 and row.get("SubType") == "7" and row.get("SkillID") not in (None, "", "0")
        )
    else:
        result["Type"] = row.get("_CATEGORY", "")
    return result

def get_item(key: str) -> dict[str, Any] | None:
    return deepcopy(_item(key))

@lru_cache(maxsize = 1)
def _stones() -> list[dict[str, Any]]:
    result = []
    for row in rows("item/Enchant.tab"):
        match = re.fullmatch(r"彩·.+\(([肆伍陆])\)", row.get("Name", ""))
        if match:
            display = _item_ui().get(row["UIID"], {})
            if not display:
                raise ValueError(f"Missing stone UI {row['UIID']}")
            result.append(
                {
                    "ID": row["ID"],
                    "Name": row["Name"],
                    "level": {
                        "肆": 4,
                        "伍": 5,
                        "陆": 6,
                    }[match[1]],
                    "icon": integer(display.get("IconID"), 1434),
                },
            )
    return result

def search_stones(level: int, keyword: str = "") -> list[dict[str, Any]]:
    return [dict(row) for row in _stones() if row["level"] == level and keyword in row["Name"]]

@lru_cache(maxsize = 1)
def _shilian() -> list[str]:
    return [
        f"{item_type}_{item_id}" for item_type in (6, 7, 8) for item_id, row in _item_table(item_type).items()
        if row["Name"].startswith("无修") and "测试" not in row["Name"]
    ]

def shilian_equips(name: str, quality: int, bind_type: int) -> list[dict[str, Any]]:
    quality = LEGACY_SHILIAN_LEVELS.get(quality, quality)
    result = []
    for key in _shilian():
        # 编号由物品原表生成，对应的物品记录必定存在。
        row = cast(dict[str, Any], _item(key))
        if row["Name"] == name and row["Level"] == quality and row["BindType"] == bind_type:
            result.append(deepcopy(row))
    return result

@lru_cache(maxsize = 1)
def _recipes() -> dict[str, dict[str, Any]]:
    result = {}
    for category in RECIPE_CATEGORIES:
        display = table(f"recipe/{category.title()}Display.tab")
        for row in rows(f"recipe/{category.title()}.tab"):
            if integer(row["ID"]) <= 0 or not integer(row.get("CreateItemIndex1")):
                continue
            recipe: dict[str, Any] = {
                key: integer(value)
                for key, value in row.items()
                if key and (key.startswith(("RequireItem", "CreateItem")) or key in ("CostVigor", "Exp"))
            }
            recipe.update(
                {
                    "ID": row["ID"],
                    "Name": row["Name"],
                    "category": category,
                    "nLevel": integer(
                        display.get(row["ID"], {}).get("nLevel"),
                        integer(row.get("RecipeLevel")),
                    ),
                    "szTip": display.get(row["ID"], {}).get("szTip", ""),
                },
            )
            item = _item(f"{recipe['CreateItemType1']}_{recipe['CreateItemIndex1']}")
            if item is None:
                raise ValueError(f"Missing recipe output: {category}:{row['ID']}")
            recipe["IconID"] = item["IconID"]
            result[f"{category}:{row['ID']}"] = recipe
    return result

def search_recipes(keyword: str) -> list[dict[str, Any]]:
    if not keyword.strip():
        return []
    records = _recipes()
    exact = [(key, row) for key, row in records.items() if row["Name"] == keyword]
    matches = exact or [(key, row) for key, row in records.items() if keyword in row["Name"]]
    return [{**row, "key": key} for key, row in matches]

def get_recipe(key: str) -> dict[str, Any] | None:
    row = _recipes().get(key)
    return dict(row) if row else None

@lru_cache(maxsize = 1)
def _npc_prices() -> dict[str, int]:
    result = {}
    currencies = (
        "CoinAmount1", "Contribution", "Prestige", "AchievementPoint", "ItemCount1", "MentorValue", "Justice",
        "ExamPrint", "ArenaAward", "ActivityAward", "TongReputation", "TongFund", "RequireCorpsValue"
    )
    restrictions = (
        "RequireAchievementRecord", "RequireLevel", "ReputeLevel", "RequireTitle", "RequireArenaLevel",
        "RequireArenaLevelExcept2v2"
    )
    for shop in rows("shop/NpcShopList.tab"):
        config = shop["ConfigFile"].replace("\\", "/").lower()
        if (not config.startswith("craft/") or shop.get("CustomShop") not in (None, "", "0")
                or shop.get("RequireForceID") not in (None, "", "0")):
            continue
        # 部分旧商店模板引用的表已经不在客户端中。
        shop_table = SHOP_TABLES.get(config.removeprefix("craft/"))
        if shop_table is None or not source_path(shop_table).is_file():
            continue
        for row in rows(shop_table):
            if (row.get("IsValid") != "1" or row.get("TabType", "").lower() != "other"
                    or integer(row.get("CountLimit")) != -1 or integer(row.get("Price")) <= 0
                    or any(integer(row.get(key)) for key in (*currencies, *restrictions))):
                continue
            key = f"5_{row['ItemIndex']}"
            price = integer(row["Price"])
            result[key] = min(result.get(key, price), price)
    return result

def npc_price(key: str) -> int | None:
    return _npc_prices().get(key)

@lru_cache(maxsize = 1)
def _npcs() -> dict[str, str]:
    return {row["ID"]: row["Name"] for row in rows("npc/NpcTemplate.tab") if row.get("Name")}

def npc_name(npc_id: int | str) -> str:
    return _npcs().get(str(npc_id), f"未知首领（{npc_id}）")

@lru_cache(maxsize = 1)
def _current_talents() -> dict[str, Any]:
    names = table("skill/MainKungfuInfo.tab", "KungfuIndex", ("name", ))
    skills = {
        (row["SkillID"], row["Level"]): {
            key: row[key]
            for key in ("Name", "IconID", "Desc")
        }
        for row in rows("skill/Skill.txt")
    }
    nouns = table("skill/Skill_Nouns.txt", "nNounID", ("szName", "szDesc"))

    def expand_nouns(text: str, seen: set[str] | None = None) -> str:
        seen = set() if seen is None else seen
        references = []

        def replace(match: re.Match[str]) -> str:
            noun = nouns.get(match[1])
            if noun is None:
                return match[0]
            if match[1] not in seen:
                seen.add(match[1])
                references.append(noun)
            return f"[{noun['szName']}]"

        text = re.sub(r"<NounID\s+(\d+)>", replace, text.replace("\\n", "\n"))
        for noun in references:
            text += f"\n[{noun['szName']}]：" + expand_nouns(noun["szDesc"], seen)
        return text

    result = defaultdict(dict)
    for row in rows("skill/TenExtraPoint.tab"):
        name = names[row["KungFuID"]]["name"]
        layer = {}
        for position in range(1, 13):
            skill_id = row.get(f"SkillID{position}")
            level = row.get(f"SkillLevel{position}")
            if not skill_id or not level:
                continue
            skill = skills.get((skill_id, level)) or skills.get((skill_id, "0"))
            if not skill:
                raise ValueError(f"Missing talent skill {skill_id}_{level}")
            layer[str(position)] = {
                "name": skill["Name"],
                "icon": skill["IconID"],
                "desc": expand_nouns(skill["Desc"]),
                "id": skill_id,
                "order": row["PointID"],
                "pos": position,
            }
        result[name][row["PointID"]] = layer
    return dict(result)

def talent_versions() -> list[str]:
    return [
        path.stem for path in sorted(TALENT_HISTORY_ROOT.glob("v*.json"))
        if re.fullmatch(r"v\d{8}(?:_\d+)?", path.stem)
    ]

@lru_cache(maxsize = 16)
def _historical_talents(version: str) -> dict[str, Any]:
    # 历史快照原本就是 JSON，直接读取原文件。
    path = TALENT_HISTORY_ROOT / f"{version}.json"
    return json.loads(path.read_text(encoding = "utf-8-sig"))

def talent_data(version: str = "") -> dict[str, Any] | None:
    if version in ("", "最新", "current", DATA_VERSION, DATA_SEASON):
        return deepcopy(_current_talents())
    versions = talent_versions()
    if version not in versions:
        matches = [name for name in versions if re.fullmatch(r"v\d{8}", version) and name.startswith(version + "_")]
        if not matches:
            return None
        version = matches[-1]
    return deepcopy(_historical_talents(version))
