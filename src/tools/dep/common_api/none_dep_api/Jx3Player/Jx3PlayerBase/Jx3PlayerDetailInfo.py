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

    def get_attributes(self, date: DateTime = None, page: AttributeType = None) -> dict[str, Jx3UserAttributeInfo]:
        '''筛选指定的属性'''
        attrs = self.attributes
        if date is not None:
            date = DateTime(date)
            xattrs = filter(lambda x: not attrs[x].is_outdated(date), attrs)
            attrs = list(xattrs)
        if page is not None:
            xattrs = filter(lambda x: attrs[x].page.attr_type & page == page, attrs)
            attrs = list(xattrs)
        return dict([x, self.attributes[x]] for x in attrs)

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
        user = Jx3PlayerInfoWithInit.from_id(server, username, cache_length=cache_length)
        return await cls.from_uid(user.serverName, user.roleId, cache_length=cache_length)

    @classmethod
    async def from_uid(cls, server: str, uid: str, cache_length: float = 86400) -> Jx3PlayerDetailInfo:
        '''通过服务器和uid从缓存或远程加载'''
        score, res = Jx3UserAttributeInfo.from_uid(uid, server, cache_length=cache_length)
        if not res:
            return res
        target = cls(uid, server, score, res)
        return target
