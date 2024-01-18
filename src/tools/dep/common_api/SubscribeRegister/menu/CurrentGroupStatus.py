from ..events import *

class CurrentGroupStatus(BaseUpdateAt):
    groups: list[str]

    def __init__(self, data: dict = None) -> None:
        super().__init__(data)
        if data is None:
            data = {}
        self.groups = data.get('groups')

    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update({
            'groups': self.groups
        })
        return result

