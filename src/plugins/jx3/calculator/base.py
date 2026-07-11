from typing import cast
from typing_extensions import Self

from src.config import Config
from src.const.jx3.kungfu import Kungfu
from src.const.prompts import PROMPT
from src.utils.database.player import search_player
from src.utils.database.attributes import JX3PlayerAttribute
from src.utils.database.classes import PlayerEquipsCache

INCOMES = {
    "无增益": [],
    "满增益": ["LDCF","CY","JF","HLSJ_1","HLSJ_2","PJ","XR","HXQJ","ZF","JHZ","CSY_SYMX","QS","LZWH","ZXYZ","XWGD","ZZM","PH","XQ","HRL"],
    "满增益风雷": ["LDCF","CY","JF","HLSJ_1","HLSJ_2","PJ","XR","HXQJ","ZF","JHZ","CSY_SYMX","QS","LZWH","ZXYZ","XWGD","NM","PH","XQ","HRL"]
}

FULL_INCOME_WITH_CONSUMABLES = {"满增益", "满增益风雷"}

MAIN_ATTR_CONSUMABLES = {
    "体质": ["FY_FOOD_VITALITY", "FY_MEDICINE_VITALITY"],
    "身法": ["FY_FOOD_AGILITY", "FY_MEDICINE_AGILITY"],
    "元气": ["FY_FOOD_SPUNK", "FY_MEDICINE_SPUNK"],
    "力道": ["FY_FOOD_STRENGTH", "FY_MEDICINE_STRENGTH"],
    "根骨": ["FY_FOOD_SPIRIT", "FY_MEDICINE_SPIRIT"],
}

ATTACK_INGOTS = {
    "Physics": ["FY_ATTACK_INGOT_PHYSICS"],
    "Magic": ["FY_ATTACK_INGOT_MAGIC"],
}
THERAPY_INGOTS = ["FY_THERAPY_INGOT"]

FEASTS = {
    "Physics": ["FYYD_PHYSICS"],
    "Magic": ["FYYD_MAGIC"],
}

# 水晶芙蓉宴是全属性宴席，T 心法需要同时吃五个属性档。
CRYSTAL_BANQUET_FEASTS = [
    "FY_CRYSTAL_BANQUET_VITALITY",
    "FY_CRYSTAL_BANQUET_AGILITY",
    "FY_CRYSTAL_BANQUET_SPUNK",
    "FY_CRYSTAL_BANQUET_STRENGTH",
    "FY_CRYSTAL_BANQUET_SPIRIT",
]

SHARED_FEASTS = ["TZY", "BLSZY", "STEAMED_FISH_PLATTER"]
VITALITY_KUNGFU_IDS = {10062, 10002, 10243, 10389}
MAGIC_TANK_KUNGFU_IDS = {10002, 10243}

FORMATIONS = {
    "无阵眼": [],
    "龙皇雪风阵": ["LHXFZ", "LHXFZ_5", "LHXFZ_SELF"],
    "千机百变阵": ["QJBBZ", "QJBBZ_SELF"],
    "苍梧引灵阵": ["CWYLZ"],
    "九宫八卦阵": ["JGBGZ"],
    "万籁金弦阵": ["WLJXZ", "WLJXZ_SELF"],
    "墟海引归阵": ["XHYGZ", "XHYGZ_SELF"],
    "北斗七星阵": ["BDQXZ"],
    "七绝逍遥阵": ["QJXYZ"],
    "天鼓雷音阵": ["TGLYZ"],
    "万蛊噬心阵": ["WGSXZ", "WGSXZ_SELF"],
    "横云破锋阵": ["HYPFZ", "HYPFZ_SELF"]
}


def _calculator_kungfu_type(kungfu_id: int, base_attr: str | None) -> str:
    """按 calculator 的心法分类选择内外功熔锭和宴席。"""
    if base_attr in {"根骨", "元气"} or kungfu_id in MAGIC_TANK_KUNGFU_IDS:
        return "Magic"
    return "Physics"


def _calculator_feast_codes(kungfu: Kungfu, base_attr: str, kungfu_type: str) -> list[str]:
    if kungfu.abbr == "T":
        return list(CRYSTAL_BANQUET_FEASTS)
    return FEASTS[kungfu_type]


def get_calculator_income_codes(income_name: str, kungfu_id: int) -> list[str]:
    income_codes = list(INCOMES[income_name])
    if income_name not in FULL_INCOME_WITH_CONSUMABLES:
        return income_codes

    kungfu = Kungfu.with_internel_id(kungfu_id, convert_to_pc=True)
    base_attr = kungfu.base
    if kungfu_id in VITALITY_KUNGFU_IDS:
        base_attr = "体质"
    if kungfu_id == 0 or base_attr is None:
        return income_codes
    kungfu_type = _calculator_kungfu_type(kungfu_id, base_attr)
    ingot_codes = THERAPY_INGOTS if kungfu.abbr == "N" else ATTACK_INGOTS[kungfu_type]
    return (
        income_codes
        + MAIN_ATTR_CONSUMABLES.get(base_attr, [])
        + ingot_codes
        + _calculator_feast_codes(kungfu, base_attr, kungfu_type)
        + SHARED_FEASTS
    )


class BaseCalculator:
    calculator_url = Config.jx3.api.calculator_url

    @classmethod
    async def with_global_role_id(cls, global_role_id: int, tag: str) -> "Self | str":
        instance = await JX3PlayerAttribute.from_database(global_role_id, tag, False)
        if instance is None:
            return PROMPT.EquipNotFound
        return cls(equip_data=instance, info=("未知", "未知"))

    @classmethod
    async def with_name(cls, name: str, server: str, tag: str) -> "Self | str":
        player_data = await search_player(role_name = name, server_name = server)
        if player_data.roleId == "":
            return PROMPT.PlayerNotExist
        await JX3PlayerAttribute.from_tuilan(player_data.roleId, player_data.serverName, player_data.globalRoleId)
        instance = await JX3PlayerAttribute.from_database(int(player_data.globalRoleId), tag, False)
        if instance is None:
            return PROMPT.EquipNotFound
        return cls(equip_data=instance, info=(name, server))
    
    def __init__(self, equip_data: JX3PlayerAttribute | None = None, info: tuple[str, str] = ("", "")):
        self.equip_data = cast(JX3PlayerAttribute, equip_data)
        self.info = info
        self.income_list = []
        self.income_ver = ""
        self.formation_list = []
        self.formation_name = ""

    @property
    def calculator_kungfu_id(self) -> int:
        kungfu_id = getattr(self, "kungfu_id", 0) or getattr(self.equip_data, "kungfu_id", 0)
        return int(kungfu_id or 0)


FIVESTONE_ITEM_ID_RANGES = (
    range(24442, 24449 + 1),
    range(24423, 24430 + 1),
)


def _is_calculator_fivestone_item_id(item_id: int) -> bool:
    return any(item_id in item_range for item_range in FIVESTONE_ITEM_ID_RANGES)


def _calculator_fivestone_item_id_from_slot_level(slot_level: int) -> int | None:
    level = slot_level + 1
    if level not in range(1, 8 + 1):
        return None
    return level + 24441


def normalize_calculator_jcl_data(jcl_data: list[list]) -> list[list]:
    normalized_data = []
    for equip_line in jcl_data:
        normalized_line = list(equip_line)
        normalized_slots = []
        equip_position = int(equip_line[0])
        for slot_index, slot_data in enumerate(equip_line[4]):
            if not isinstance(slot_data, (list, tuple)) or len(slot_data) < 2:
                normalized_slots.append(slot_data)
                continue

            slot_type = int(slot_data[0])
            slot_value = int(slot_data[1])
            if equip_position in {0, 1, 2} and slot_index >= 3:
                normalized_slots.append(list(slot_data))
                continue

            if slot_type == 0 or _is_calculator_fivestone_item_id(slot_value):
                normalized_slots.append(list(slot_data))
                continue

            item_id = _calculator_fivestone_item_id_from_slot_level(slot_type)
            if item_id is None:
                normalized_slots.append(list(slot_data))
            else:
                normalized_slots.append([5, item_id])
        normalized_line[4] = normalized_slots
        normalized_data.append(normalized_line)

    ring_lines = [line for line in normalized_data if int(line[0]) in {6, 7}]
    if len(ring_lines) == 2 and {int(line[0]) for line in ring_lines} != {6, 7}:
        # Some equipment exports use the same position for both rings.  The
        # calculator needs the two physical slots to remain distinguishable.
        ring_lines[0][0] = 6
        ring_lines[1][0] = 7

    primary_weapon_line = next(
        (line for line in normalized_data if int(line[0]) == 0),
        None,
    )
    if primary_weapon_line is not None:
        for equip_line in normalized_data:
            if int(equip_line[0]) == 1:
                equip_line[3] = primary_weapon_line[3]
                equip_line[4] = [list(slot) if isinstance(slot, list) else slot for slot in primary_weapon_line[4]]
    return normalized_data
