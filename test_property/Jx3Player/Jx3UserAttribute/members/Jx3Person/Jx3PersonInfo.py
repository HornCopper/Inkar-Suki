from .Jx3Qixue import *


class Jx3PersonInfo:
    def __init__(self, data: dict) -> None:
        if data is None:
            data = {}
        self.load_data(data)

    def map_data(self, data: dict):
        if 'qixueList' not in data:
            return data
        data['qixue'] = data.get('qixueList') or []
        return data

    def load_data(self, data: dict):
        self.map_data(data)
        self.atAgilityBase: int = int(data.get('atAgilityBase'))
        self.atLifeAdditional: int = int(data.get('atLifeAdditional'))
        self.atManaAdditional: int = int(data.get('atManaAdditional'))
        self.atSpiritBase: int = int(data.get('atSpiritBase'))
        self.atSpunkBase: int = int(data.get('atSpunkBase'))
        self.atStrengthBase: int = int(data.get('atStrengthBase'))
        self.atVitalityBase: int = int(data.get('atVitalityBase'))
        self.body: int = int(data.get('body'))
        '''形体'''
        self.experience: int = int(data.get('experience'))
        '''当前经验值'''
        self.level: int = int(data.get('level'))
        '''当前等级'''
        self.maxAssistExp: int = int(data.get('maxAssistExp'))
        self.maxAssistTimes: int = int(data.get('maxAssistTimes'))
        self.maxStamina: int = int(data.get('maxStamina'))
        self.maxThew: int = int(data.get('maxThew'))
        self.parryBaseRate: int = int(data.get('parryBaseRate'))
        self.title: str = data.get('title')
        self.qixue = [Qixue(x) for x in data.get('qixue')]

    def to_dict(self):
        result = copy.deepcopy(self.__dict__)
        result['qixue'] = [x.to_dict() for x in self.qixue]
        return result
