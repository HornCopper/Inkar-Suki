from sgtpyutils.datetime import *


class BaseUpdateAt:
    def __init__(self, data: dict = None) -> None:
        if data is None:
            return
        self.load_data(data)

    def load_data(self, data: dict):
        self.updateAt: float = data.get("updateAt") or DateTime().timestamp()
        """数据更新时间"""

    @overload
    def is_outdated(self, target: DateTime) -> bool:
        """按保质期计算"""
        ...

    @overload
    def is_outdated(self, target: float = 86400) -> bool:
        """按保质最长间隔计算"""
        ...

    def is_outdated(self, target: DateTime = 86400):
        if isinstance(target, float) or isinstance(target, int):
            target = self.updateAt + float(target)
        if isinstance(target, DateTime):
            target = target.timestamp()
        return DateTime().timestamp() > target

    def to_dict(self) -> dict:
        return {
            "updateAt": self.updateAt,
        }
