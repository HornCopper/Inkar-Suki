from typing import overload


class UserPanel:
    @overload
    def __init__(self, data: dict) -> None:
        ...

    @overload
    def __init__(self, name: str, percent: bool, value: float) -> None:
        ...

    def __init__(self, name: str, percent: bool = None, value: float = None) -> None:
        if isinstance(name, dict):
            percent = name.get('percent') or False
            value = name.get('value') or 0
            name = name.get('name')
        self.name: str = name  # 属性名称
        self.percent: bool = percent  # 是否是百分比
        self.value: float = value  # 数值

