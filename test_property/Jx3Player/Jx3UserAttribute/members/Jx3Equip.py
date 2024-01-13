from .Jx3Icon import *
from src.tools.utils import *
from src.tools.file import *


class WCommonEnchant:
    '''
    大附魔属性
    '''
    lock = threading.RLock()
    ranges: list[tuple[str, int, int]] = None

    def __init__(self, id: str, quality: int) -> None:
        self.id = id
        self.quality = quality

    @property
    def name(self):
        with self.lock:
            if not self.ranges:
                path = pathlib2.Path(__file__).parent.joinpath(
                    'map.common-enchant-static.json').as_posix()
                self.ranges = json.loads(read(path))
        q = self.quality
        def f(x): return x[1] < q and x[2] > q
        return extensions.find(self.ranges, f) or '未知'


class EquipIcon(Jx3Icon):
    ...


class Jx3Equip:
    def __init__(self, data: dict) -> None:
        self.load_data(data)

    def map_data(self, data: dict):
        base = {
            'item_id': data.get('ID'),
            'uid': data.get('UID'),
            'name': data.get('Name'),
            'icon': data.get('Icon'),
            'set': {
                'total': data.get('SetList'),
                'current': data.get('SetListMap')
            },
            'color_index': int(data.get('Color') or 0),
            'stone': data.get('FiveStone'),
            'level': data.get('Level'),
            'quality': data.get('Quality'),
            'quality_ext': data.get('IncreaseQuality'),
            'belongs':  {
                'kungfu': data.get('BelongKungfu'),
                'school': data.get('BelongSchool'),
            },
            'score': data.get('Score'),
            'score_ext': data.get('JinglianScore'),
        }

        t1 = data.get('WCommonEnchant') or {}
        t2 = data.get('WPermanentEnchant') or {}
        enchant = {
            'wCommonEnchant': t1.get('Id'),  # 判断是否有大附魔
            'wPermanentEnchant': t2.get('Name'),
            'strengthLevel': data.get('StrengthLevel'),
            'maxStrengthLevel': data.get('MaxStrengthLevel'),
        }

        result = {}
        result.update(base)
        result.update(enchant)
        result.update(data)
        return result

    def load_data(self, data: dict):
        if 'Name' in data:
            data = self.map_data(data)

        self.item_id = data.get('item_id')
        '''uid'''
        self.uid = data.get('uid')
        '''uid'''

        self.name = data.get('name')
        '''装备名称'''
        self.icon = EquipIcon(data.get('icon'))
        '''图标url'''
        self.set = data.get('set')
        '''套装列表'''
        self.color_index = data.get('color_index')
        self.stone = data.get('stone')
        '''五行石 [{Level,Name}]'''
        self.level = int(data.get('level'))
        '''游戏等级'''
        self.quality = int(data.get('quality'))
        '''品质'''
        self.quality_ext = int(data.get('quality_ext'))
        '''精炼附加品质'''
        self.score = int(data.get('score'))
        '''装分'''
        self.score_ext = int(data.get('score_ext'))
        '''精炼附加装分'''
        self.belongs = data.get('belongs')
        '''所属心法
        {
            kungfu # 心法（按,分割）列表
            school # 门派/精简/通用
        }
        '''
        self.wCommonEnchant = WCommonEnchant(data.get('wCommonEnchant'), self.quality)
        ''' # 大附魔 {Desc:'',Id:'11111'}'''
        self.wPermanentEnchant = data.get('wPermanentEnchant')
        ''' 小附魔 {Attributes,Name} '''
        self.strengthLevel = int(data.get('strengthLevel'))
        '''强化等级'''
        self.maxStrengthLevel = int(data.get('maxStrengthLevel'))
        '''最高强化等级'''

        pass

    def to_dict(self):
        return {
            'item_id': self.item_id,
            'uid': self.uid,
            'name': self.name,
            'icon': self.icon.filename,
            'set': self.set,
            'color_index': self.color_index,
            'stone': self.stone,
            'level': self.level,
            'quality': self.quality,
            'quality_ext': self.quality_ext,
            'score': self.score,
            'score_ext': self.score_ext,
            'belongs': self.belongs,
            'wCommonEnchant': self.wCommonEnchant.id,
            'wPermanentEnchant': self.wPermanentEnchant,
            'strengthLevel': self.strengthLevel,
            'maxStrengthLevel': self.maxStrengthLevel,
        }
