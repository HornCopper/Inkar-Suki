from __future__ import annotations
from .HorseItem import *
from .MapData import *
from .MapHorseData import *
from .HorseRecord import *
from .HorseRecordType import *
from src.tools.dep import *


class HorseEventRecord(HorseItem):
    def __init__(self, parent: HorseRecord, name: str, minute: int) -> None:
        if parent is None:
            return  # 手动构建

        if not isinstance(parent, HorseRecord):
            raise InvalidArgumentException("parent->HorseRecord")
        self.timestamp: DateTime = DateTime(parent.timestamp) + minute * 60e3

        names = name.split("/")
        self.load_by_raw_data(parent.id, names, parent.map_id)

    def load_by_raw_data(self, parent_id: str, horses_id: list[str], map_id: str):
        self.id = parent_id
        self.horses = [HorseInfo.from_id(x) for x in horses_id]
        self.horses = [x for x in self.horses if x]
        self.horses_id = [x.key for x in self.horses]

        self.map_id = map_id
        self.map_data: MapData = MapData.from_id(map_id)
        self.map_horse_data: MapHorseData = MapHorseData.from_id(map_id)

    @property
    def outdated(self):
        return super().outdated

    def to_dict(self):
        return {
            "id": self.id,
            "horses": self.horses_id,
            "timestamp": self.timestamp.timestamp(),
            "map": self.map_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> HorseEventRecord:
        target = cls(None, None, None)
        target.timestamp = DateTime(data.get("timestamp"))
        parent_id = data.get("id")
        horses = data.get("horses")
        map_id = data.get("map")
        target.load_by_raw_data(parent_id, horses, map_id)
        return target


class HorseRecords:
    @overrides
    def __init__(self, server: str) -> None:
        ...

    @overrides
    def __init__(self, server: str, records: list[dict]) -> None:
        ...

    def __init__(self, server: str, records: list[dict] = None) -> None:
        if server is None:
            return
        self.server = server
        if records is not None:
            self.load_records(records)

    @staticmethod
    def sort(items: list[HorseRecord]):
        items = extensions.distinct(items, lambda x: x.id)
        items = list(filter(lambda x: not x.outdated, items))
        new_items = sorted(items, key=lambda x: x.timestamp.timestamp(), reverse=True)  # 按时间戳降序排序
        return list(new_items)

    def load_records(self, records: list[dict]):
        items = [HorseRecord(x) for x in records]
        self.records = HorseRecords.sort(items)
        valid_recordss = self.filter_by_map(self.records)
        self.valid_records: List[HorseEventRecord] = extensions.flat(valid_recordss)

    def merge_records(self, target: HorseRecords) -> HorseRecords:
        """合并和去重"""
        if not target:
            return self
        x = HorseRecords(self.server)
        records = self.records + target.records
        x.records = self.sort(records)
        valid_records = self.valid_records + target.valid_records
        x.valid_records = self.sort(valid_records)
        return x

    def filter_by_map(self, records: list[HorseRecord]) -> list[HorseEventRecord]:
        result: dict[str, list[HorseEventRecord]] = {}  # 地图-马名:次数 保存2次

        def handle_horse(x: HorseRecord):
            if not x.map_id:
                return False
            if not x.subtype == HorseRecordType.NpcChat.value:
                return False
            if not x.items:  # 检查是否是有效数据
                return False

            for record in x.items:
                name = record[0]
                minute = record[1]
                key = f"{x.map_id}@{name}"
                if not result.get(key):
                    result[key] = []
                r = HorseEventRecord(x, name, minute)
                result[key].append(r)
            return True
        for x in records:
            handle_horse(x)
        return [result[x] for x in result]

    def to_dict(self):
        return {
            "records": [x.to_dict() for x in self.records],
            "valid_records": [x.to_dict() for x in self.valid_records],
        }

    @classmethod
    def from_dict(cls, data: dict) -> HorseRecords:
        target = cls(None)

        def convert_record(cls, items: list[dict]) -> list[cls]:
            if not items:
                return []
            return [cls.from_dict(x) for x in items]
        target.records = convert_record(HorseRecord, data.get("records"))
        target.valid_records = convert_record(HorseEventRecord, data.get("valid_records"))
        return target
