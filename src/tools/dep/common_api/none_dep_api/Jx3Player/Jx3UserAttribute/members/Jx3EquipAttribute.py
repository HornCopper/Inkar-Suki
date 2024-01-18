from .Jx3EquipAttributeType import *
from .Jx3AttributeType import *  # 待解耦


class Jx3EquipAttribute:
    primary_attributes = {
        '会心': '会',
        '无双': '无',
        '破防': '破防',
        '破招': '破招',
        '加速': '速',
        '御劲': '御',
        '化劲': '化',
        '治疗成效': '疗'
    }
    attribute_types = {
        '无': AttributeType.DPS | AttributeType.PVE,
        '破防': AttributeType.DPS,
        '破招': AttributeType.DPS | AttributeType.PVE,
        '御': AttributeType.TANK,
        '化': AttributeType.TANK | AttributeType.PVP,
        '疗': AttributeType.HPS,
    }

    def __init__(self, data: dict) -> None:
        if data is None:
            data = {}
        self.load_data(data)
        pass

    def map_data(self, data: dict):
        if 'Desc' not in data:
            return data
        data['name'] = data.get('Desc')

        attrib = data.get('Attrib') or {}
        data['desc'] = attrib.get('GeneratedMagic')

        data['score'] = data.get('Increase')

        data['value_max'] = data.get('Param1Max') or 0
        data['value_min'] = data.get('Param2Min') or data['value_max']
        return data

    def load_data(self, data: dict):
        self.map_data(data)
        self.name = data.get('name')
        '''atVitalityBase..'''
        self.desc = data.get('desc')
        '''体质提高4456'''
        self.score: int = data.get('score')
        '''装分提升'''
        self.value_max = int(data.get('value_max'))
        '''属性最小增加数值'''
        self.value_min = int(data.get('value_min'))
        '''属性最大增加数值'''

    @property
    def primary_attribute(self) -> str:
        desc = self.desc
        for x in Jx3EquipAttribute.primary_attributes:
            if x in desc:
                return Jx3EquipAttribute.primary_attributes[x]
        return ''  # 其他属性不显示

    @property
    def suffix(self) -> Jx3EquipAttributeType:
        result = Jx3EquipAttributeType.无
        if '攻击' in self.desc:
            result |= Jx3EquipAttributeType.伤
        if '治疗' in self.desc:
            result |= Jx3EquipAttributeType.疗
        if '防御' in self.desc:
            result |= Jx3EquipAttributeType.御
        if '化劲' in self.desc:
            result |= Jx3EquipAttributeType.化
        return result

    def to_dict(self):
        return {
            'name': self.name,
            'desc': self.desc,
            'score': self.score,
            'value_max': self.value_max,
            'value_min': self.value_min,
        }
