from __future__ import annotations
from src.tools.utils import *
from ...common import *
from .members.Jx3Equip import *
from .members import *
from .IJx3UserAttributeFactory import *


class BaseJx3UserProperty(BaseUpdateAt):
    factory: IJx3UserAttributeFactory
    c_path = f'{bot_path.common_data_full}jx3_users'
    cache: dict[str, BaseUpdateAt] = filebase_database.Database(
        c_path,
        serializer=lambda data: dict([x, data[x].to_dict()] for x in data),
        deserializer=lambda data: dict([x, BaseUpdateAt(data[x])] for x in data),
    ).value
    '''key:lastupdate'''

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
            data = BaseJx3UserProperty.map_data(data)
        super().load_data(data)
        self.equips: list[Jx3Equip] = [Jx3Equip(x) for x in (data.get('equips'))]
        self.kungfu: Kungfu = Kungfu(data.get('kungfu'))
        self.matchDetail: MatchDetail = MatchDetail(data.get('matchDetail'))
        self.person: Jx3PersonInfo = Jx3PersonInfo(data.get('person'))
        self.panel: list[UserPanel] = [UserPanel(x) for x in data.get('panel')]
        self.score: int = data.get('score')
        return self

    @classmethod
    def from_uid(cls, uid: str, server: str, cache_length: float = 0) -> dict[str, BaseJx3UserProperty]:
        '''dict[装分:属性值]'''
        key = f'{server}@{uid}'
        target = BaseJx3UserProperty.cache.get(key)
        if target and not target.is_outdated(cache_length):
            return cls.from_cache(uid, server)

        # 重新加载
        task = cls.factory._get_property_by_uid(uid, server)
        current_prop: BaseJx3UserProperty = ext.SyncRunner.as_sync_method(task)

        # 记录更新时间
        BaseJx3UserProperty.cache[key] = BaseUpdateAt(current_prop.__dict__)
        # 存入缓存
        result = cls.from_cache(uid, server)
        result[str(current_prop.score)] = current_prop
        return result

    @classmethod
    def get_db_from_cache(cls, uid: str, server: str) -> BaseJx3UserProperty:
        key = f'{server}@{uid}'
        db = filebase_database.Database(
            f'{cls.c_path}{os.sep}{key}',
            serializer=lambda data: dict([x, data[x].to_dict()] for x in data),
            deserializer=lambda data: dict([x, BaseJx3UserProperty(data[x])] for x in data),
        )
        return db

    @classmethod
    def from_cache(cls, uid: str, server: str) -> BaseJx3UserProperty:
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
