from .members import *
from ...common import *

class BaseJx3UserSummary(BaseUpdateAt):
    """记录更新时间和最后一次获取的装分"""

    def __init__(self, data: dict = None) -> None:
        super().__init__(data)

    def load_data(self, data: dict):
        super().load_data(data)
        self.score = int(data.get("score") or 0)

    def to_dict(self) -> dict:
        result = {
            "score": self.score,
        }
        result.update(super().to_dict())
        return result


jeat = Jx3EquipAttributeType


class BaseJx3UserAttributePage:
    types: list[tuple[AttributeType, str]] = [
        (AttributeType.Unknown, "当前"),
        (AttributeType.PVP | AttributeType.DPS, "PVP-DPS"),
        (AttributeType.PVE | AttributeType.DPS, "PVE-DPS"),
        (AttributeType.PVP | AttributeType.HPS, "PVP-HPS"),
        (AttributeType.PVE | AttributeType.HPS, "PVE-HPS"),
        (AttributeType.PVP | AttributeType.TANK, "PVP-TANK"),
        (AttributeType.PVE | AttributeType.TANK, "PVE-TANK"),
        (AttributeType.PVX, "寻宝娱乐"),
        (AttributeType.FLY, "轻功"),
    ]
    types_mapper = {
        "dps": 2,
        "hps": 4,
        "t": 6,
    }
    eq_attrs_mapper = {
        jeat.伤: AttributeType.DPS,
        jeat.疗: AttributeType.HPS,
        jeat.御: AttributeType.TANK,
        jeat.伤 | jeat.化: AttributeType.DPS | AttributeType.PVP,
        jeat.疗 | jeat.化: AttributeType.HPS | AttributeType.PVP,
        jeat.御 | jeat.化: AttributeType.TANK | AttributeType.PVP,
        jeat.化: AttributeType.PVP,
        "dps": AttributeType.DPS,
        "hps": AttributeType.HPS,
        "t": AttributeType.TANK,
    }

    def __init__(self) -> None:
        self.attr_type = AttributeType.Unknown
        self.equip_unmatch: list[Jx3Equip] = []

    def to_dict(self):
        return {
            "equip_unmatch": [x.item_id for x in self.equip_unmatch],
            "attr_type": self.attr_type.value,
        }
