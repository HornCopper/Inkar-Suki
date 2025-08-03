from dataclasses import dataclass, field
from typing import Literal, Any

from src.utils.analyze import Locations
from src.utils.network import Request

from .base import BaseCalculator

subtype_locations = {
    0: 0,
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 8,
    7: 9,
    8: 10,
    9: 11,
    10: 12
}

Attributes = {
    "atPhysicsAttackPowerBase": "外功攻击",
    "atPhysicsCriticalStrike": "外功会心",
    "atPhysicsOvercomeBase": "外功破防",
    "atPhysicsCriticalDamagePowerBase": "外功会心效果",
    "atPhysicsShieldBase": "外功防御",

    "atSolarAndLunarAttackPowerBase": "阴阳内功攻击",
    "atSolarAndLunarCriticalStrike": "阴阳内功会心",
    "atSolarAndLunarOvercomeBase": "阴阳内功破防",
    "atSolarAndLunarOvercomeBase": "阴阳内功会心效果",

    "atNeutralAttackPowerBase": "混元内功攻击",
    "atNeutralCriticalStrike": "混元内功会心",
    "atNeutralOvercomeBase": "混元内功破防",
    "atNeutralCriticalDamagePowerBase": "混元内功会心效果",

    "atSolarAttackPowerBase": "阳性内功攻击",
    "atSolarCriticalStrike": "阳性内功会心",
    "atSolarOvercomeBase": "阳性内功破防",
    "atSolarCriticalDamagePowerBase": "阳性内功会心效果",

    "atLunarAttackPowerBase": "阴性内功攻击",
    "atLunarCriticalStrike": "阴性内功会心",
    "atLunarOvercomeBase": "阴性内功破防",
    "atLunarCriticalDamagePowerBase": "阴性内功会心效果",

    "atPoisonAttackPowerBase": "毒性内功攻击",
    "atPoisonCriticalStrike": "毒性内功会心",
    "atPoisonOvercomeBase": "毒性内功破防",
    "atPoisonCriticalDamagePowerBase": "毒性内功会心效果",

    "atMagicAttackPowerBase": "内功攻击",
    "atMagicOvercome": "内功破防",
    "atMagicCriticalStrike": "内功会心",
    "atMagicCriticalDamagePowerBase": "内功会心效果",
    "atMagicShield": "内功防御",

    "atStrainBase": "无双",
    "atSurplusValueBase": "破招",
    "atHasteBase": "加速",

    "atAllTypeOvercomeBase": "全破防",
    "atAllTypeCriticalStrike": "全会心",
    "atAllTypeCriticalDamagePowerBase": "全会心效果"
}

def parse_attr(equip_data: dict[str, Any]) -> list[str]:
    attr = []
    for num in range(1, 17):
        key = f"Magic{num}Key"
        if key not in equip_data:
            break
        attr_name = Attributes.get(equip_data[key], "")
        if attr_name != "":
            attr.append(attr_name)
    return attr

@dataclass
class EquipInfo:
    name: str
    quality: int
    location: str
    item_id: int
    attr: list[str] = field(default_factory=list)
    subkind: Literal["精简", "散件", "特效"] = "散件"

    def __eq__(self, other):
        if not isinstance(other, EquipInfo):
            return False
        return (self.attr == other.attr and
                self.name == other.name and
                self.quality == other.quality and
                self.location == other.location)

    def __hash__(self):
        return hash((self.attr, self.name, self.quality, self.location))

async def get_equip_list(equip_name: str) -> list[EquipInfo]:
    url = BaseCalculator.calculator_url + f"/equip?equip_name={equip_name}"
    data = (await Request(url).get()).json()
    results = []
    for each_equip in data:
        result = EquipInfo(
            name = each_equip["Name"],
            quality = int(each_equip["Level"]),
            attr = parse_attr(each_equip),
            item_id = int(each_equip["ID"]),
            location = Locations[subtype_locations[int(each_equip["SubType"])]],
            subkind = "特效" if ("atSkillEventHandler" in each_equip.values()) else ("精简" if each_equip["BelongSchool"] == "精简" else "散件")
        )
        if result not in results:
            results.append(result)
    return results