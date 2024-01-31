from src.tools.dep.common_api.none_dep_api.common.EntityWithUpdateAt import *
class CurrentGroupStatus(BaseUpdateAt):
    groups: list[str]

    def __init__(self, data: dict = None) -> None:
        if data is None:
            data = {}
        super().__init__(data)
        self.groups = data.get("groups")

    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update({
            "groups": self.groups
        })
        return result

