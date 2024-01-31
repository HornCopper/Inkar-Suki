
from .Jx3EquipAttribute import *
from src.tools.utils import *
from src.tools.file import *

import json


class WCommonEnchant:
    """
    大附魔属性
    """
    lock = threading.Lock()
    ranges: list[tuple[str, int, int]] = None
    suffix_enum = {
        "帽": "帽",
        "衣": "衣",
        "腰": "腰",
        "鞋": "鞋",
        "裤子": None,
        "项链": None,
        "戒指": None,
        "腰坠": None,
    }

    def __init__(self, id: str, quality: int, attributes: list[Jx3EquipAttribute], sub_kind: str) -> None:
        self.id = id
        self.quality = quality
        self.attributes = attributes
        self.sub_kind = sub_kind
        self._name = Ellipsis

    @property
    def core_name(self):
        with self.lock:
            if not self.ranges:
                path = pathlib2.Path(__file__).parent.joinpath(
                    "map.common-enchant-static.json").as_posix()
                self.ranges = json.loads(read(path))
        q = self.quality
        def f(x): return x[1] < q and x[2] > q
        core_name = extensions.find(self.ranges, f) or "大附魔"
        return core_name

    @property
    def name(self):
        if self._name is not Ellipsis:
            return self._name
        core_name = self.core_name

        core_type: Jx3EquipAttributeType = extensions.find(
            self.attributes, lambda x: x.suffix is not Jx3EquipAttributeType.无)
        if not core_type:
            self._name = None
            return self._name
        self._name = f"{core_name}·{core_type.name}·{self.suffix}"
        return self._name

    @property
    def suffix(self):
        t = self.sub_kind
        d = WCommonEnchant.suffix_enum
        result: str = extensions.find(list(d), lambda x: d[x] in t)
        return d[result]

