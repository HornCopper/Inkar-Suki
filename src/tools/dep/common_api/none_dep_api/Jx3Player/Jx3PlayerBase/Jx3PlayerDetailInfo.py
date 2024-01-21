from __future__ import annotations
from ..Jx3UserAttribute import *
from .Jx3PlayerLoader import *


class Jx3PlayerDetailInfo:
    def __init__(self, uid: str, server: str, current_score: str, attributes: dict[str, Jx3UserAttributeInfo], user: Jx3PlayerInfo = None) -> None:
        self.current_score = str(current_score)
        self.attributes = attributes
        '''dict[str,Jx3UserAttributeInfo] 装分:属性'''
        self.uid = uid
        self.server = server
        self.__user = user
        self.err_msg = None

    @property
    def latest_attrs(self) -> dict[str, str]:
        '''获取最新数据
        @return dict[类型enum,装分]'''
        result = BaseJx3UserAttribute.cache_latest_attr.get(self.key)
        if not result:
            return {}
        return result

    @property
    def key(self):
        return f'{self.server}@{self.uid}'

    def get_attributes_history_by_attr_type(self, start: DateTime = None, end: DateTime = None) -> list[tuple[int, int]]:
        '''获取历史装分变动记录'''
        raise NotImplemented()

    def get_attributes_by_attr_type(self, attr_type: AttributeType) -> Jx3UserAttributeInfo:
        '''直接通过缓存获取最新配置'''
        key = self.key
        result = None
        if his := BaseJx3UserAttribute.cache_latest_attr.get(key):
            if isinstance(attr_type, AttributeType):
                attr_type = attr_type.value
            attr_score = his.get(str(attr_type))
            if attr_score and int(attr_score) > 0:
                result = self.attributes.get(attr_score)

        if result is None:
            # TODO 后期数据全部完成缓存后应删除
            if result := self.get_attributes_by_filter(attr_type=attr_type):
                result = result[0]  # 取装分最高者
        return result

    def get_attributes_by_filter(self, date: DateTime = None, attr_type: AttributeType = None, pageIndex: int = 0, pageSize: int = 10) -> list[Jx3UserAttributeInfo]:
        '''筛选指定的属性 TODO 筛选页面对PVE-DPS和HPS不准确
        @return 按装分降序列表'''
        attrs = [self.attributes[x] for x in self.attributes]

        if date is not None:
            date = DateTime(date)
            attrs = filter(lambda x: not x.is_outdated(date), attrs)
            attrs = list(attrs)
        if attr_type is not None:
            attrs = filter(lambda x: x.page.attr_type & attr_type == attr_type, attrs)
            attrs = list(attrs)

        return self.split_page(attrs, pageIndex, pageSize)

    def split_page(self, attrs_score: list[int], pageIndex: int = 0, pageSize: int = 200) -> list[Jx3UserAttributeInfo]:
        sorted_attrs = sorted([int(str(x)) for x in attrs_score], key=lambda x: x, reverse=True)
        start = pageIndex * pageSize

        if len(sorted_attrs) < start:
            return []
        scores = [str(x) for x in sorted_attrs[start:start+pageSize]]
        result = [self.attributes[x] for x in list(scores)]
        return result

    @property
    def user(self):
        if self.__user:
            return self.__user
        uid = self.uid
        self.__user = Jx3PlayerInfoWithInit.from_uid(uid)
        return self.__user

    @classmethod
    async def from_auto(cls, server: str, username_or_uid: str, cache_length: float = 86400) -> Jx3PlayerDetailInfo:
        '''如果传入数值，则按uid，否则按id'''
        username_or_uid = str(username_or_uid)
        if len(username_or_uid) > 5 and checknumber(username_or_uid):
            return await cls.from_uid(server, username_or_uid, cache_length)
        return await cls.from_username(server, username_or_uid, cache_length)

    @classmethod
    async def from_username(cls, server: str, username: str, cache_length: float = 86400) -> Jx3PlayerDetailInfo:
        '''通过服务器和id从缓存或远程加载'''
        user = Jx3PlayerInfoWithInit.from_id(server, username, cache_length=7*86400)  # 一周内不更新
        if not user.roleId:
            tar = Jx3PlayerDetailInfo(None, server, None, {}, user)
            tar.err_msg = PROMPT_UserNotExist
            return tar
        return await cls.from_uid(user.serverName, user.roleId, cache_length=cache_length)

    @classmethod
    async def from_uid(cls, server: str, uid: str, cache_length: float = 86400) -> Jx3PlayerDetailInfo:
        '''通过服务器和uid从缓存或远程加载'''
        score, res = Jx3UserAttributeInfo.from_uid(uid, server, cache_length=cache_length)
        if not res:
            return res
        target = cls(uid, server, score, res)
        return target
