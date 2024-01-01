from __future__ import annotations
from .HorseItem import *
from .MapData import *
from .MapHorseData import *
from .HorseRecord import *
from .HorseRecordType import *
from src.tools.dep import *


class HorseEventRecord(HorseItem):
    def __init__(self, parent: HorseRecord, name: str, minute: int) -> None:
        if not isinstance(parent, HorseRecord):
            raise InvalidArgumentException('parent->HorseRecord')
        self.id = parent.id
        names = name.split('/')
        self.horses = [HorseInfo.from_id(x) for x in names]
        self.horses = [x for x in self.horses if x]
        self.horses_id = [x.key for x in self.horses]
        if not self.horses:
            pass
        self.timestamp: DateTime = DateTime(parent.timestamp) + minute * 60e3

        self.map_id = parent.map_id
        self.map_data: MapData = MapData.from_id(parent.map_id)

        self.map_horse_data: MapHorseData = MapHorseData.from_id(parent.map_id)

    @property
    def outdated(self):
        return super().outdated

    def to_dict(self):
        return {
            'id': self.id,
            'horses': self.horses_id,
            'timestamp': self.timestamp.timestamp(),
            'map': self.map_id,
        }


class HorseRecords:
    @overrides
    def __init__(self, server: str) -> None:
        ...

    @overrides
    def __init__(self, server: str, records: list[dict]) -> None:
        ...

    def __init__(self, server: str, records: list[dict] = None) -> None:
        self.server = server
        if records:
            self.load_records(records)

    @staticmethod
    def sort(items: list[HorseRecord]):
        items = extensions.distinct(items, lambda x: x.id)
        items = list(filter(lambda x: not x.outdated, items))
        return sorted(items, key=lambda x: x.timestamp.timestamp(), reverse=True) # 按时间戳降序排序

    def load_records(self, records: list[dict]):
        items = [HorseRecord(x) for x in records]
        self.records = HorseRecords.sort(items)
        valid_recordss = self.filter_by_map(self.records)
        self.valid_records: List[HorseEventRecord] = extensions.flat(valid_recordss)

    def merge_records(self, target: HorseRecords) -> HorseRecords:
        '''合并和去重'''
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
            if not x.sub_type == HorseRecordType.NpcChat.value:
                return False
            if not x.items:  # 检查是否是有效数据
                return False

            for record in x.items:
                name = record[0]
                minute = record[1]
                key = f'{x.map_id}@{name}'
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
            'records': [x.to_dict() for x in self.records],
            'valid_records': [x.to_dict() for x in self.valid_records],
        }
