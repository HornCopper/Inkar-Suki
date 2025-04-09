from src.utils.database.operation import set_group_settings, get_group_settings
from src.utils.time import Time

class Blacklist:
    def __init__(self, name: str, group_id: int | str, submit_id: int = 0):
        self._name = name
        self._group_id = str(group_id)
        self._submit_id = submit_id

    @property
    def status(self) -> bool | str:
        group_data: list[dict[str, str]] = get_group_settings(self._group_id, "blacklist")
        self._data = group_data
        for each in group_data:
            if each["ban"] == self._name:
                return each["reason"]
        return False
    
    def add(self, reason: str = ""):
        if self.status:
            return False
        self._data.append(
            {
                "ban": self._name,
                "reason": reason,
                "source": str(self._submit_id),
                "time": str(Time().raw_time)
            }
        )
        set_group_settings(self._group_id, "blacklist", self._data)
        
    def remove(self):
        if not self.status:
            return False
        set_group_settings(self._group_id, "blacklist", [dict_ for dict_ in self._data if dict_["ban"] != self._name])
