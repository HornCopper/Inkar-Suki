from .Jx3Icon import *
from .Jx3Stone import *
from .Jx3EquipAttribute import *
from src.tools.utils import *
from src.tools.file import *


class WCommonEnchant:
    '''
    大附魔属性
    '''
    lock = threading.RLock()
    ranges: list[tuple[str, int, int]] = None
    suffix_enum = {
        '帽': '帽',
        '衣': '衣',
        '腰': '腰',
        '鞋': '鞋',
        '裤子': None,
        '项链': None,
        '戒指': None,
        '腰坠': None,
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
                    'map.common-enchant-static.json').as_posix()
                self.ranges = json.loads(read(path))
        q = self.quality
        def f(x): return x[1] < q and x[2] > q
        core_name = extensions.find(self.ranges, f) or '大附魔'
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
        self._name = f'{core_name}·{core_type.name}·{self.suffix}'
        return self._name

    @property
    def suffix(self):
        t = self.sub_kind
        d = WCommonEnchant.suffix_enum
        result: str = extensions.find(list(d), lambda x: d[x] in t)
        return d[result]


class EquipIcon(Jx3Icon):
    ...


class Jx3Equip:
    uc_pos = {
        '4': 1,  # 头
        '3': 2,  # 衣
        '8': 3,  # 腰
        '12': 4,  # 手
        '10': 5,  # 裤
        '11': 6,  # 鞋
        '5': 7,  # 项链
        '9': 8,  # 坠
        '6': 9,  # 戒指1
        '7': 10,  # 戒指2
        '2': 11,  # 暗器
        '0': 12,  # 武器1
        '1': 13,  # 武器2
    }

    def __init__(self, data: dict) -> None:
        self.load_data(data)

    def map_data(self, data: dict):
        index = Jx3Equip.uc_pos.get(data.get('UcPos'))
        base = {
            'index': index,
            'item_id': data.get('ID'),
            'uid': data.get('UID'),
            'name': data.get('Name'),
            'icon': data.get('Icon'),
            'set': {
                'total': data.get('SetList'),
                'current': data.get('SetListMap')
            },
            'color_index': int(data.get('Color') or 0),
            'stones': data.get('FiveStone') or [],
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
            'wCommonEnchant': t1.get('ID'),  # 判断是否有大附魔
            'wPermanentEnchant': t2.get('Name'),
            'strengthLevel': data.get('StrengthLevel'),
            'maxStrengthLevel': data.get('MaxStrengthLevel'),
        }

        # '商店：陈只鱼 — 浪客行·装备'
        way_to_fetch = data.get('equipBelongs') or []
        way_to_fetch = [x.get('source') for x in way_to_fetch]

        result = {
            'way_to_fetch': way_to_fetch,
            'attributes': data.get('ModifyType') or [],
            'sub_kind': base['icon'].get('SubKind'),
        }
        result.update(base)
        result.update(enchant)
        return result

    def load_data(self, data: dict):
        if 'Name' in data:
            data = self.map_data(data)
        self.index = data.get('index')
        '''排序'''
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
        self.stones = [Jx3Stone(x) for x in data.get('stones')]
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
        self.sub_kind = data.get('sub_kind')
        '''部位分类'''

        self.attributes = [Jx3EquipAttribute(x) for x in data.get('attributes')]
        '''提供属性加成'''

        common_enchant = data.get('wCommonEnchant')
        self.wCommonEnchant = common_enchant and WCommonEnchant(
            common_enchant, self.quality, self.attributes, self.sub_kind)
        ''' # 大附魔 {Desc:'',Id:'11111'}'''
        self.wPermanentEnchant = data.get('wPermanentEnchant')
        ''' 小附魔 {Attributes,Name} '''
        self.strengthLevel = int(data.get('strengthLevel'))
        '''强化等级'''
        self.maxStrengthLevel = int(data.get('maxStrengthLevel'))
        '''最高强化等级'''

        self.way_to_fetch: list[str] = data.get('way_to_fetch')
        '''获得途径'''
        pass

    def to_dict(self):
        return {
            'index': self.index,
            'item_id': self.item_id,
            'uid': self.uid,
            'name': self.name,
            'icon': self.icon.filename,
            'set': self.set,
            'color_index': self.color_index,
            'stones': [x.to_dict() for x in self.stones],
            'level': self.level,
            'quality': self.quality,
            'quality_ext': self.quality_ext,
            'score': self.score,
            'score_ext': self.score_ext,
            'belongs': self.belongs,
            'wCommonEnchant': self.wCommonEnchant and self.wCommonEnchant.id,
            'wPermanentEnchant': self.wPermanentEnchant,
            'strengthLevel': self.strengthLevel,
            'maxStrengthLevel': self.maxStrengthLevel,
            'attributes': [x.to_dict() for x in self.attributes],
            'way_to_fetch': self.way_to_fetch,
        }
