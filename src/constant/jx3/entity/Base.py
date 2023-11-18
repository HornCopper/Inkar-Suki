from __future__ import annotations
from sgtpyutils.logger import logger

class Aliasable:
    '''
    基础
    '''
    __static_dict: dict[str, any] = {}

    alias: list[str]
    '''别称'''
    name: str
    '''名称'''

    def register_alias(self):
        '''
        将本T的别称和正式称呼注册到全局缓存
        '''
        for alias in self.alias:
            Aliasable.__static_dict[alias] = self
        Aliasable.__static_dict[self.name] = self

    @classmethod
    def from_alias(cls, alias: str):
        return Aliasable.__static_dict.get(alias)
