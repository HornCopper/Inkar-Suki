from __future__ import annotations
import enum


class AttributeType(enum.IntFlag):
    Unknown = 0
    PVP = 2 << 1
    PVE = 2 << 2
    PVX = 2 << 3

    DPS = 2 << 11
    HPS = 2 << 12
    TANK = 2 << 13

    FLY = 2 << 21

    def warning(self):
        '''判断类型是否重复，重复则说明不合理'''
        v = self.value

        group_1 = [AttributeType.PVP, AttributeType.PVE, AttributeType.PVX]
        counter_1 = len(filter(lambda x: x & v == x, group_1))

        group_2 = [AttributeType.DPS, AttributeType.HPS, AttributeType.TANK]
        counter_2 = len(filter(lambda x: x & v == x, group_2))

        return counter_1 > 1 or counter_2 > 1

    @classmethod
    def from_alias(cls, alias: str) -> AttributeType:
        alias = str(alias).lower()
        result = AttributeType.Unknown
        for type in AttributeType:
            if type.name.lower() in alias:
                result |= type
        return result
