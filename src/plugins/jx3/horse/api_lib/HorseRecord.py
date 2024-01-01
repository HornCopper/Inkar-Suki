from __future__ import annotations
import re
from src.tools.dep import *
from .HorseItem import *


class HorseRecord(HorseItem):
    re_valid_time = re.compile(r'下一匹(\S*)出世还有(\S*)分钟', re.RegexFlag.MULTILINE)
    re_valid_immediate = re.compile(r'下一匹(\S*)即将出世', re.RegexFlag.MULTILINE)

    def __init__(self, data: dict) -> None:
        self.data = data
        self.id = data.get('id')
        self.content = data.get('content')
        self.map_name = data.get('map_name')
        self.map_id = str(data.get('map_id'))
        self.timestamp = DateTime(data.get('time'))
        self.sub_type = data.get('subtype')
        self.__init = False

    @property
    def items(self) -> list[tuple[str, int]]:
        if self.__init:
            return self.__items
        self.__init = True
        return self.get_items()

    @property
    def outdated(self) -> bool:
        return super().outdated

    def get_items(self) -> list[tuple[str, int]]:
        '''获取有效信息'''
        valid_time = HorseRecord.re_valid_time.findall(self.content)
        valid_immediate = HorseRecord.re_valid_immediate.findall(self.content)
        valid_immediate = [[x, 0] for x in valid_immediate] # 默认出现时间为0分钟
        result = valid_time + valid_immediate
        result = [[x[0], int(x[1])] for x in result]
        self.__items = result
        return result

    def to_dict(self):
        return {
            'id': self.id,
            'map': self.map_id,
            'timestamp': self.timestamp.timestamp(),
            'subtype': self.sub_type
        }
