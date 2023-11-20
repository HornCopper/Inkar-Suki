from .Base import *
import enum


class AttrType(enum.Enum):
    none = 0
    damage = 1
    tank = 2
    heal = 3


__objects = {
    AttrType.damage: lambda attr: ["面板攻击", "基础攻击", "会心", "会心效果", "加速", attr, "破防", "无双", "破招", "最大气血值", "御劲", "化劲"],
}


class PrimaryAttr(Aliasable):
    '''主属性'''
    database = './config.primary_attr'
    type: AttrType = AttrType.none

    @property
    def objects(self) -> list[str]:
        return __objects.get(self.type)
