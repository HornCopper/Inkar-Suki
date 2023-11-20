from __future__ import annotations
from sgtpyutils.logger import logger


class Aliasable:
    '''
    基础
    '''
    __static_dict: dict[str, str, any] = {}

    alias: list[str]
    '''别称'''
    name: str
    '''名称'''

    def _get_dict(self):
        '''
        获取当前类型对应的字典
        '''
        m = self.__module__
        x = Aliasable.__static_dict.get(m)
        if x is None:
            Aliasable.__static_dict[m] = {}
            return self._get_dict()
        return x

    def register_alias(self):
        '''
        将本T的别称和正式称呼注册到全局缓存
        '''
        d = self._get_dict()
        for alias in self.alias:
            d[alias] = self
        d[self.name] = self

    @classmethod
    def from_alias(cls, alias: str):
        return cls()._get_dict().get(alias)
