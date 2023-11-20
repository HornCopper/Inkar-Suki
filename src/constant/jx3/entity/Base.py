from __future__ import annotations
from sgtpyutils.logger import logger
from sgtpyutils.database import filebase_database

from sgtpyutils.extensions.clazz import *
import pathlib2
current = pathlib2.Path(__file__).parent


class Databased:
    database: str = 'not implement'

    @classmethod
    def _register_type(cls):
        logger.info(f'database init for [{cls.__name__}] path:{cls.database}')
        target = str(current.joinpath(cls.database))
        db_entity = filebase_database.Database(target).value  # 心法数据
        def func(x): return [x.get('name'), dict2obj(cls(), x)]
        dict_entity = dict([func(x) for x in db_entity])  # 心法字典
        for x in dict_entity:
            dict_entity[x].register_alias()


class Aliasable(Databased):
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
