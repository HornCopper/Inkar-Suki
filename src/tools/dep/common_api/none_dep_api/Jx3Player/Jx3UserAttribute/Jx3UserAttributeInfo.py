from __future__ import annotations
from src.tools.utils import *
from src.constant.jx3 import *
from .BaseJx3UserAttributePage import *
from .IJx3UserAttributeFactory import *


class BaseJx3UserAttribute(BaseUpdateAt):
    factory: IJx3UserAttributeFactory
    c_path = f'{bot_path.common_data_full}jx3_users'
    cache: dict[str, BaseJx3UserSummary] = filebase_database.Database(
        c_path,
        serializer=lambda data: dict([x, data[x].to_dict()] for x in data),
        deserializer=lambda data: dict([x, BaseJx3UserSummary(data[x])] for x in data),
    ).value
    '''key:lastupdate'''

    c_latest_path = f'{c_path}_latest'
    cache_latest_attr: dict[str, dict[str, str]] = filebase_database.Database(c_latest_path).value
    '''key:user-key key2:attr_type'''

    @property
    def page(self) -> BaseJx3UserAttributePage:
        '''
        判断装备含有 攻击、防御、治疗
        判断装备心法类型
        判断当前心法类型
        判断装备化劲是否>0
        '''
        result = BaseJx3UserAttributePage()

        # 按心法匹配当前类型
        kun_type = self.kungfu.type or 'dps'
        result.attr_type |= BaseJx3UserAttributePage.eq_attrs_mapper.get(kun_type)

        # 内功或外功
        kun_ptype = self.kungfu.practice_type
        kun_ptype = kun_ptype if isinstance(kun_ptype, list) else [kun_ptype]

        # 属性常用常数
        att_default = AttributeType.Unknown
        att_dict = Jx3EquipAttribute.attribute_types

        def handle_primary_attr(equip: Jx3Equip):
            if equip.index == 12:
                return  # 忽略主武器
            # if equip.index == 13:
            #     return  # 忽略副武器

            # 按装备主属性判断
            primary_attr: AttributeType = extensions.reduce(
                equip.attributes,
                lambda prev, cur: prev | (att_dict.get(cur.primary_attribute) or att_default),
                att_default,
            )
            result.attr_type |= primary_attr

        equip_unmatch = []

        def handle_kunfu_attr(equip: Jx3Equip):
            '''判断异常装备，装备适用心法是否与当前心法相同'''
            e_kun = self.equips[0].belongs.get('kungfu') or ''
            e_kun = e_kun.split(',')

            if e_kun[0] in kun_ptype:
                return  # 当为精简时先匹配内功外功

            match = extensions.find(e_kun, lambda x: x in self.kungfu.alias)
            if not match:
                equip_unmatch.append(equip)  # 心法不符

        def handle_enchant(equip: Jx3Equip):
            '''通过大附魔判断'''
            enchant_suffix = equip.enchant_suffix
            if not enchant_suffix:
                return
            result.attr_type |= BaseJx3UserAttributePage.eq_attrs_mapper.get(enchant_suffix)

        for equip in self.equips:
            handle_enchant(equip)
            handle_kunfu_attr(equip)
            handle_primary_attr(equip)

        result.equip_unmatch = equip_unmatch
        return result

    def __init__(self, data: dict = None) -> None:
        super().__init__(data)
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
        if not uid:
            return None, None
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
        if current_prop and current_prop.score > 0:
            # 只记录有装分的属性
            score = str(current_prop.score)
            current_prop.record_new_data(result, score)
            # 记录更新时间
            BaseJx3UserAttribute.cache[key] = BaseJx3UserSummary(current_prop.to_dict())

            # 记录当前主属性
            if latest := BaseJx3UserAttribute.cache_latest_attr[key]:
                pass
            else:
                latest = {}
                BaseJx3UserAttribute.cache_latest_attr[key] = latest
            latest[str(current_prop.page.attr_type.value)] = score

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

    def record_new_data(self, result: dict[str, BaseJx3UserAttribute], score: str):
        '''检查数据完整性并写入'''
        prev = result.get(score)
        if prev is None:
            result[score] = self
            return  # 首次记录则直接记录

        if self.person.qixue:
            result[score] = self
            return  # 数据有效则直接记录

        # 按装分排序
        prevs = sorted(list(result), key=lambda x: int(x), reverse=True)
        prevs = list(prevs)

        # 筛选有奇穴的
        prevs = filter(lambda x: result[x].person.qixue, prevs)  # 过滤有效奇穴的
        prevs = list(prevs)

        # 取得该奇穴
        prev = result.get(prevs[0]) if prevs else None
        if prev:
            prev = result[prev]
            self.person.qixue = prev.person.qixue  # 使用之前的记录
        else:
            logger.warning(f'用户{self.person.to_dict()}当前无任何有效奇穴可用')

        result[score] = self

    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update({
            'equips': [x.to_dict() for x in self.equips],
            'kungfu': self.kungfu and self.kungfu.name,
            'matchDetail': self.matchDetail.__dict__,
            'person': self.person.to_dict(),
            'panel': [x.__dict__ for x in self.panel],
            'score': self.score,
            'page': self.page.to_dict(),
        })
        return result

    def to_view(self) -> dict:
        result = self.to_dict()
        result.update({
            'kungfu': self.kungfu.to_dict(),
            'equips': [x.to_view() for x in self.equips],
        })
        return result
