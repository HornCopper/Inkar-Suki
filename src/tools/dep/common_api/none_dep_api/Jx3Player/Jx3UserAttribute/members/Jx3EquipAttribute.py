import enum


class Jx3EquipAttributeType(enum.IntFlag):
    无 = 0
    伤 = 1
    疗 = 2
    御 = 3


class Jx3EquipAttribute:
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
    def suffix(self) -> Jx3EquipAttributeType:
        if '攻击' in self.desc:
            return Jx3EquipAttributeType.伤
        if '治疗' in self.desc:
            return Jx3EquipAttributeType.疗
        if '防御' in self.desc:
            return Jx3EquipAttributeType.御
        return Jx3EquipAttributeType.无

    def to_dict(self):
        return {
            'name': self.name,
            'desc': self.desc,
            'score': self.score,
            'value_max': self.value_max,
            'value_min': self.value_min,
        }
