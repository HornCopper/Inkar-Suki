from __future__ import annotations
from src.tools.utils import *
from ...common import *
from .members.Jx3Equip import *
from .members import *
from .IJx3UserAttributeFactory import *
from src.constant.jx3 import *


class BaseJx3UserSummary(BaseUpdateAt):
    '''记录更新时间和最后一次获取的装分'''

    def __init__(self, data: dict = None) -> None:
        super().__init__(data)

    def load_data(self, data: dict):
        super().load_data(data)
        self.score = int(data.get('score') or 0)

    def to_dict(self) -> dict:
        result = {
            'score': self.score,
        }
        result.update(super().to_dict())
        return result


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


jeat = Jx3EquipAttributeType


class BaseJx3UserAttributePage:
    types = [
        AttributeType.Unknown,
        AttributeType.PVP | AttributeType.DPS,
        AttributeType.PVE | AttributeType.DPS,
        AttributeType.PVP | AttributeType.HPS,
        AttributeType.PVE | AttributeType.HPS,
        AttributeType.PVP | AttributeType.TANK,
        AttributeType.PVE | AttributeType.TANK,
        AttributeType.PVX,
        AttributeType.FLY,
    ]
    types_mapper = {
        'dps': 2,
        'hps': 4,
        't': 6,
    }
    eq_attrs_mapper = {
        jeat.伤: AttributeType.DPS,
        jeat.疗: AttributeType.HPS,
        jeat.御: AttributeType.TANK,
        jeat.伤 | jeat.化: AttributeType.DPS | AttributeType.PVP,
        jeat.疗 | jeat.化: AttributeType.HPS | AttributeType.PVP,
        jeat.御 | jeat.化: AttributeType.TANK | AttributeType.PVP,
        jeat.化: AttributeType.PVP,
        'dps': AttributeType.DPS,
        'hps': AttributeType.HPS,
        't': AttributeType.TANK,
    }

    def __init__(self) -> None:
        self.attr_type = AttributeType.Unknown
        self.equip_unmatch: list[Jx3Equip] = []

    def to_dict(self):
        return {
            'equip_unmatch': [x.item_id for x in self.equip_unmatch],
            'attr_type': self.attr_type.value,
        }


class BaseJx3UserAttribute(BaseUpdateAt):
    factory: IJx3UserAttributeFactory
    c_path = f'{bot_path.common_data_full}jx3_users'
    cache: dict[str, BaseJx3UserSummary] = filebase_database.Database(
        c_path,
        serializer=lambda data: dict([x, data[x].to_dict()] for x in data),
        deserializer=lambda data: dict([x, BaseJx3UserSummary(data[x])] for x in data),
    ).value
    '''key:lastupdate'''

    @property
    def page(self) -> BaseJx3UserAttributePage:
        '''
        判断装备含有 攻击、防御、治疗
        判断装备心法类型
        判断当前心法类型
        判断装备化劲是否>0
        '''
        result = BaseJx3UserAttributePage()
        equip_unmatch = []
        for equip in self.equips:
            if equip.index == 12:
                continue  # 忽略主武器
            # if equip.index == 13:
            #     continue  # 忽略副武器

            ###
            enchant_suffix = equip.enchant_suffix
            if enchant_suffix:
                result.attr_type |= BaseJx3UserAttributePage.eq_attrs_mapper.get(enchant_suffix)

            ###
            e_kun = self.equips[0].belongs.get('kungfu') or ''
            e_kun = e_kun.split(',')
            match = extensions.find(e_kun, lambda x: x in self.kungfu.alias)
            if not match:
                equip_unmatch.append(equip)  # 心法不符

            ###
            kun_type = self.kungfu.type or 'dps'
            result.attr_type |= BaseJx3UserAttributePage.eq_attrs_mapper.get(kun_type)

        result.equip_unmatch = equip_unmatch
        return result

    def __init__(self, data: dict = None) -> None:
        super().__init__(data)
        self.load_data(data)
        pass

    @staticmethod
    def map_data(data: dict) -> dict:
        '''将api数据转换为本地数据'''
        mapped = {
            'equips': (data.get('Equips') or []),
            'kungfu': data.get('Kungfu').get('Name'),
            'matchDetail': (data.get('MatchDetail') or []),
            'person': data.get('Person'),
            'panel': (data.get('PersonalPanel') or []),
            'score': data.get('TotalEquipsScore'),
        }
        mapped.update(data)
        return mapped

    def load_data(self, data: dict):
        if 'TotalEquipsScore' in data:
            data = BaseJx3UserAttribute.map_data(data)
        super().load_data(data)
        self.equips: list[Jx3Equip] = [Jx3Equip(x) for x in (data.get('equips'))]
        self.kungfu: Kunfu = Kunfu.from_alias(data.get('kungfu'))
        self.matchDetail: MatchDetail = MatchDetail(data.get('matchDetail'))
        self.person: Jx3PersonInfo = Jx3PersonInfo(data.get('person'))
        self.panel: list[UserPanel] = [UserPanel(x) for x in data.get('panel')]
        self.score: int = data.get('score')
        return self

    @classmethod
    def from_uid(cls, uid: str, server: str, cache_length: float = 0) -> tuple[str, dict[str, BaseJx3UserAttribute]]:
        '''
        @return:
            str:当前装分
            dict[装分:属性值]'''
        key = f'{server}@{uid}'
        target = BaseJx3UserAttribute.cache.get(key)
        if target and not target.is_outdated(cache_length):
            return target.score, cls.from_cache(uid, server)

        # 重新加载
        task = cls.factory._get_attribute_by_uid(uid, server)
        current_prop: BaseJx3UserAttribute = ext.SyncRunner.as_sync_method(task)
        # 存入缓存
        result = cls.from_cache(uid, server)
        score = '0'  # 默认值
        if current_prop.score > 0:
            # 只记录有装分的属性
            score = str(current_prop.score)
            result[score] = current_prop
            # 记录更新时间
            BaseJx3UserAttribute.cache[key] = BaseJx3UserSummary(current_prop.to_dict())
            pass
        elif len(list(result)) == 0:
            # 从未有过任何装分
            return None, None

        return score, result

    @classmethod
    def get_db_from_cache(cls, uid: str, server: str) -> BaseJx3UserAttribute:
        key = f'{server}@{uid}'
        db = filebase_database.Database(
            f'{cls.c_path}{os.sep}{key}',
            serializer=lambda data: dict([x, data[x].to_dict()] for x in data),
            deserializer=lambda data: dict([x, BaseJx3UserAttribute(data[x])] for x in data),
        )
        return db

    @classmethod
    def from_cache(cls, uid: str, server: str) -> dict[str, BaseJx3UserAttribute]:
        db = cls.get_db_from_cache(uid, server)
        return db.value

    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update({
            'equips': [x.to_dict() for x in self.equips],
            'kungfu': self.kungfu.name,
            'matchDetail': self.matchDetail.__dict__,
            'person': self.person.to_dict(),
            'panel': [x.__dict__ for x in self.panel],
            'score': self.score,
            'page': self.page.to_dict(),
        })
        return result
