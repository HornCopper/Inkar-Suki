from __future__ import annotations
from src.tools.dep.data_server import *
from src.tools.utils import *
from src.tools.dep.jx3.Jx3ApiResponse import *
from src.tools.config import Config
from ..Jx3UserAttribute import *
from .Jx3PlayerLoader import *


class Jx3PlayerDetailInfo:
    def __init__(self, uid: str, server: str, attribute: Jx3UserAttributeInfo, user: Jx3PlayerInfo = None) -> None:
        self.attribute = attribute
        self.uid = uid
        self.server = server
        self.__user = user

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
            return cls.from_uid(server, username_or_uid, cache_length)
        return cls.from_username(server, username_or_uid, cache_length)

    @classmethod
    async def from_username(cls, server: str, username: str, cache_length: float = 86400) -> Jx3PlayerDetailInfo:
        '''通过服务器和id从缓存或远程加载'''
        user = Jx3PlayerInfoWithInit.from_id(server, username, cache_length=cache_length)
        return await cls.from_uid(user.serverName, user.roleId)

    @classmethod
    async def from_uid(cls, server: str, uid: str, cache_length: float = 86400) -> Jx3PlayerDetailInfo:
        '''通过服务器和uid从缓存或远程加载'''
        res = Jx3UserAttributeInfo.from_uid(uid, server, cache_length=cache_length)
        if not res:
            return res
        target = cls(uid, server, res)
        return target
