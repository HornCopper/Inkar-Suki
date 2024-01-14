from __future__ import annotations
from src.tools.utils import *
from ...common import *
from .members.Jx3Equip import *
from .members import *
from .IJx3UserAttributeFactory import *
from src.constant.jx3 import *

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

    def __init__(self) -> None:
        self.attr_type = AttributeType.Unknown
        self.page: int = 0


class BaseJx3UserAttribute(BaseUpdateAt):
    factory: IJx3UserAttributeFactory
    c_path = f'{bot_path.common_data_full}jx3_users'
    cache: dict[str, BaseUpdateAt] = filebase_database.Database(
        c_path,
        serializer=lambda data: dict([x, data[x].to_dict()] for x in data),
        deserializer=lambda data: dict([x, BaseUpdateAt(data[x])] for x in data),
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
        pass
        return result

    def __init__(self, data: dict = None) -> None:
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
    def from_uid(cls, uid: str, server: str, cache_length: float = 0) -> dict[str, BaseJx3UserAttribute]:
        '''dict[装分:属性值]'''
        key = f'{server}@{uid}'
        target = BaseJx3UserAttribute.cache.get(key)
        if target and not target.is_outdated(cache_length):
            return cls.from_cache(uid, server)

        # 重新加载
        task = cls.factory._get_attribute_by_uid(uid, server)
        current_prop: BaseJx3UserAttribute = ext.SyncRunner.as_sync_method(task)

        # 存入缓存
        result = cls.from_cache(uid, server)
        if current_prop.score > 0:
            # 只记录有装分的属性
            result[str(current_prop.score)] = current_prop
            # 记录更新时间
            BaseJx3UserAttribute.cache[key] = BaseUpdateAt(current_prop.__dict__)
        elif len(list(result)) == 0:
            # 从未有过任何装分
            return None

        return result

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
    def from_cache(cls, uid: str, server: str) -> BaseJx3UserAttribute:
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
        })
        return result
