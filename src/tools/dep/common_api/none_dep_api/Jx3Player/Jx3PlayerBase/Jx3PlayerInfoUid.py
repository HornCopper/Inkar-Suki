from __future__ import annotations
from src.tools.dep.data_server import *
from src.tools.utils import *
from src.tools.dep.jx3.Jx3ApiResponse import *
from src.tools.config import Config
_bot = Config.bot
_token = Config.jx3api_globaltoken


class Jx3PlayerInfoUid:
    def __init__(self, data: dict = None) -> None:
        if data is None:
            return
        self.load_data(data)

    def load_data(self, data: dict):
        self.updateAt = data.get('updateAt') or DateTime().timestamp()
        '''数据更新时间'''
        self.roleId = data.get('roleId')
        '''区服大区'''

    def to_dict(self):
        return copy.deepcopy(self.__dict__)

