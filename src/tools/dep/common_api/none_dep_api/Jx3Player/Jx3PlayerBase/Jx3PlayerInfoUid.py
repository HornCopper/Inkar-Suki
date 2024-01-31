from __future__ import annotations
from src.tools.utils import *
class Jx3PlayerInfoUid:
    def __init__(self, data: dict = None) -> None:
        if data is None:
            return
        self.load_data(data)

    def load_data(self, data: dict):
        self.updateAt = data.get("updateAt") or DateTime().timestamp()
        """数据更新时间"""
        self.roleId = data.get("roleId")
        """区服大区"""

    def to_dict(self):
        return copy.deepcopy(self.__dict__)

