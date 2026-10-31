"""Classify client drop records using table fields and explicit ID exceptions.

Names, descriptions and icons are presentation data, never classification inputs.
The client does not encode crystal/iron roles or the contents of scripted weapon
boxes in Other.tab, so those distinctions are reviewed by composite item ID.
Unknown items stay out of simulated pools until a rule can identify them.
"""

from enum import Enum

from src.utils.jx3_tables import integer


class LootKind(str, Enum):
    WEAPON = "weapon"
    WEAPON_BOX = "weapon_box"
    FINAL_WEAPON_BOX = "final_weapon_box"
    EQUIPMENT_BOX = "equipment_box"
    ARMOR = "armor"
    SIMPLIFIED = "simplified"
    EFFECT_EQUIP = "effect_equip"
    EFFECT_WEAPON = "effect_weapon"
    EFFECT_PENDANT = "effect_pendant"
    BRAND = "brand"
    GENERAL_BRAND = "general_brand"
    TEMP_ENCHANT = "temp_enchant"
    PERMANENT_ENCHANT = "permanent_enchant"
    ENCHANT_BOX = "enchant_box"
    CRAFT_MATERIAL = "craft_material"
    IRON = "iron"
    CRYSTAL = "crystal"
    STONE = "stone"
    TREASURE = "treasure"
    BOOK = "book"
    EXTRA_PEERLESS = "extra_peerless"
    PEERLESS = "peerless"
    APPEARANCE = "appearance"
    UNKNOWN = "unknown"


# Verified against client 1.6.0.10022. Keys include the item table type.
ITEM_KIND_OVERRIDES = {
    **{f"5_{idx}": LootKind.IRON for idx in (6629, 10359, 19283, 25829, 31600, 37104, 47901, 71568, 89975)},
    **{f"5_{idx}": LootKind.CRYSTAL for idx in (6630, 10360, 19284, 25830, 31601, 37103, 47902, 71569, 89976)},
    **{
        f"5_{idx}": LootKind.FINAL_WEAPON_BOX for idx in (
            42095, 42097, 44461, 44463, 48131, 50805, 50807, 54521, 54523, 68032,
            68034, 75318, 78493, 78495, 82073, 82076, 86011, 86014, 89729,
        )
    },
    **{f"5_{idx}": LootKind.TREASURE for idx in (81930, 81931, 82184, 82185, 86006, 86035)},
    # Legacy tokens use SubType=0; legacy permanent enchants have had their
    # EnchantID cleared in the current client. Do not treat them as containers.
    **{f"5_{idx}": LootKind.BRAND for idx in (*range(21326, 21376), *range(34093, 34098))},
    **{
        f"5_{idx}": LootKind.PERMANENT_ENCHANT for idx in (
            *range(78066, 78085), *range(81581, 81601), *range(85556, 85576),
        )
    },
    "5_76660": LootKind.ENCHANT_BOX,
    "5_36491": LootKind.CRAFT_MATERIAL,
    # Paired weapon containers verified through their client item-link IDs;
    # their weapon slot is independent of the simplified/effect gear slot.
    **{
        f"5_{idx}": LootKind.EFFECT_WEAPON for idx in (
            29178, 30248, 31578, 32701, 33469, 35533, 37096, 39109, 41908, 44448,
            47449, 47458, 54177, 68037, 71885, 78503, 81870, 85806, 89713,
        )
    },
}

# Effect handler IDs do not carry a damage/healing/tank enum. These verified
# Enchant.tab IDs retain the existing 3:1:1 weighting without reading names.
DAMAGE_ENCHANT_IDS = frozenset((*range(16675, 16680), *range(16690, 16695)))

EFFECT_ATTRIBUTES = {"atSkillEventHandler", "atExecuteScript", "atSetEquipmentRecipe"}
HEAL_TANK_ATTRIBUTES = {"atTherapyPowerBase", "atToughnessBase", "atActiveThreatCoefficient"}


def attribute_types(item: dict) -> set[str]:
    return {attribute.get("Desc", "") for attribute in item.get("ModifyType", [])}


def has_equip_effect(item: dict) -> bool:
    return bool(item.get("SkillID") or attribute_types(item) & EFFECT_ATTRIBUTES)


def is_heal_or_tank(item: dict) -> bool:
    return item.get("MagicKind") in ("治疗", "防御") or bool(attribute_types(item) & HEAL_TANK_ATTRIBUTES)


def equipment_slot(item: dict) -> tuple[int, int]:
    return integer(item.get("ItemType")), integer(item.get("SubType"), -1)


def enchant_weight(item: dict) -> int:
    return 3 if item.get("EnchantID") in DAMAGE_ENCHANT_IDS else 1


def classify_loot_item(item: dict) -> LootKind:
    if item.get("id") in ITEM_KIND_OVERRIDES:
        return ITEM_KIND_OVERRIDES[item["id"]]
    item_type, subtype = equipment_slot(item)
    if item_type == 10:
        return LootKind.PEERLESS
    if item_type in (6, 7, 8):
        # Mounts, pets, ornaments and horse gear share the trinket table.
        if item_type == 8 and subtype not in (4, 5, 7):
            return LootKind.PEERLESS
        if item.get("IsEffectPendant"):
            return LootKind.EFFECT_PENDANT
        if has_equip_effect(item):
            if item_type == 6 and subtype == 0 and item.get("BelongSchool") != "精简":
                return LootKind.EFFECT_WEAPON
            return LootKind.EFFECT_EQUIP
        if item.get("BelongSchool") == "精简":
            return LootKind.SIMPLIFIED
        if item_type == 6 and subtype == 0:
            return LootKind.WEAPON
        if item.get("ModifyType") and item.get("BelongSchool"):
            return LootKind.ARMOR
        return LootKind.UNKNOWN
    if item_type != 5:
        return LootKind.UNKNOWN

    enchant = item.get("Enchant", {})
    target = integer(enchant.get("DestItemSubType"), -1)
    if item.get("EnchantID") and enchant:
        if integer(enchant.get("Time")) > 0 and target in (2, 3, 6, 9, 10):
            return LootKind.TEMP_ENCHANT
        if integer(enchant.get("Time")) == 0 and target in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
            return LootKind.PERMANENT_ENCHANT
    if (item.get("Genre") == 7 and item.get("AucGenre") == 13
            and not item.get("EnchantID") and not item.get("ScriptName")):
        return LootKind.ENCHANT_BOX

    script = item.get("ScriptName", "").replace("\\", "/").rsplit("/", 1)[-1].lower()
    if script == "raid牌子包.lua":
        return LootKind.GENERAL_BRAND
    if script == "raid秘境武器包.lua":
        return LootKind.WEAPON_BOX
    if script == "藏剑武器包.lua":
        return LootKind.WEAPON
    if script == "剧情模式10人装备包.lua":
        return LootKind.EQUIPMENT_BOX
    if item.get("Type") == "副本掉落道具" and subtype == 6:
        return LootKind.BRAND
    if item.get("AucGenre") == 15 and item.get("AucSubType") in (1, 6):
        return LootKind.STONE
    if item.get("AucGenre") == 10 and item.get("AucSubType") == 10:
        return LootKind.CRAFT_MATERIAL
    if item.get("Type") == "生活技能特殊材料":
        return LootKind.CRAFT_MATERIAL
    if item.get("Genre") == 24 and subtype == 2:
        return LootKind.BOOK
    if item.get("Type") in ("特殊武器任务", "阅读材料", "江湖百态"):
        return LootKind.EXTRA_PEERLESS
    if item.get("Type") == "Act_运营及版本道具" or item.get("Genre") == 18:
        return LootKind.APPEARANCE
    if item.get("Genre") == 21 or item.get("Type") == "玩具":
        return LootKind.PEERLESS
    return LootKind.UNKNOWN


def group_loot(items: list[dict]) -> dict[LootKind, list[dict]]:
    pools: dict[LootKind, list[dict]] = {kind: [] for kind in LootKind}
    seen = set()
    for item in items:
        key = item["id"]
        if key in seen:
            continue
        seen.add(key)
        pools[classify_loot_item(item)].append(item)
    return pools
