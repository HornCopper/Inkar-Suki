from typing import List, Any

from src.utils.database import db
from src.utils.database.classes import BannedUser

class Ban:
    def __init__(self, user_id: int | str):
        self._user_id = user_id

    @property
    def _data(self) -> list:
        data: List[BannedUser] | Any = db.where_all(BannedUser()) or []
        return data

    @property
    def status(self) -> bool:
        """
        该`user_id`是否被封禁。

        Returns:
            status (bool): 封禁状态。
        """
        for each_ban in self._data:
            each_ban: BannedUser
            if str(each_ban.user_id) == str(self._user_id):
                return True
        return False
    
    def ban(self, reason: str = "") -> bool:
        """
        封禁某个`user_id`。

        Args:
            reason (str): 封禁原因，可留空。

        Returns:
            status (bool): 若为`False`则封禁失败（重复封禁）。
        """
        if self.status:
            return False
        db.save(BannedUser(user_id=int(self._user_id), reason=reason))
        return True
    
    def unban(self) -> bool:
        """
        解封某个`user_id`

        Returns:
            status (bool): 若为`False`则解封失败（尚未封禁）。
        """
        if not self.status:
            return False
        db.delete(BannedUser(), "user_id = ?", self._user_id)
        return True