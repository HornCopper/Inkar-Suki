from dataclasses import dataclass, field
from typing import Literal, Any

from src.utils.analyze import Locations
from src.utils.jx3_attributes import AttributesFull
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
    10: 12,
}

def parse_attr(equip_data: dict[str, Any]) -> list[str]:
    attr = []
    for num in range(1, 17):
        key = f"Magic{num}Key"
        if key not in equip_data:
            break
        attr_name = AttributesFull.get(equip_data[key], "")
        if attr_name != "":
            attr.append(attr_name)
    return attr

@dataclass
class EquipInfo:
    name: str
    quality: int
    location: str
    item_id: int
    location_code: int
    attr: list[str] = field(default_factory = list)
    subkind: Literal["精简", "散件", "特效"] = "散件"

    def __eq__(self, other):
        if not isinstance(other, EquipInfo):
            return False
        return (
            self.attr == other.attr and self.name == other.name and self.quality == other.quality
            and self.location == other.location
        )

    def __hash__(self):
        return hash((self.attr, self.name, self.quality, self.location))

@dataclass
class EnchantInfo:
    name: str
    enchant_id: int
    desc: str
    location_code: int
    is_common: bool = False  # 是否为大附魔

    def __eq__(self, other):
        if not isinstance(other, EnchantInfo):
            return False
        return (self.enchant_id == other.enchant_id)

    def __hash__(self):
        return hash((self.enchant_id, self.name, self.desc, self.location_code))

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
            location_code = subtype_locations[int(each_equip["SubType"])],
            location = Locations[subtype_locations[int(each_equip["SubType"])]],
            subkind = "特效" if ("atSkillEventHandler" in each_equip.values()) else
            ("精简" if each_equip["BelongSchool"] == "精简" else "散件"),
        )
        if result not in results:
            results.append(result)
    return results

async def get_enchant_list(enchant_name: str) -> list[EnchantInfo]:
    url = BaseCalculator.calculator_url + f"/enchant?enchant_name={enchant_name}"
    data = (await Request(url).get()).json()
    results = []
    if data["code"] != 200:
        return results
    for each_enchant in data["data"]:
        if not each_enchant["Name"].startswith("彩·"):
            location_code = subtype_locations[int(each_enchant["DestItemSubType"])]
        else:
            location_code = 0
        result = EnchantInfo(
            name = each_enchant["Name"],
            enchant_id = int(each_enchant["ID"]),
            desc = each_enchant["AttriName"],
            location_code = location_code,
            is_common = (each_enchant["Time"] == "60"),
        )
        if result not in results:
            results.append(result)
    return results
