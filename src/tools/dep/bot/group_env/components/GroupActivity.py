from ..GroupConfig import *


class GroupActivity(GroupConfig):
    '''统计群聊热度'''
    KEY_Slient = 'activity.slient_count'

    def __init__(self, group_id: str, config: str = 'jx3group', config_root: dict[str, GroupConfigInfo] = None, log: bool = False) -> None:
        super().__init__(group_id, config, config_root, log)

    def update_statistics_slient(self):
        prev = self.total_general()
        if prev > 0:
            self.mgr_property(GroupActivity.KEY_Slient, 0)
            return # 沉寂天数归零

        count = self.mgr_property(GroupActivity.KEY_Slient)
        count += 1
        self.mgr_property(GroupActivity.KEY_Slient, count)

    def update_base(self, key: str, value_change: int = None) -> list[int]:
        result = super().mgr_property(f'activity.{key}')
        if isinstance(value_change, int):
            day = DateTime().day
            result[day-1] += value_change
            result[day % 31] = 0  # 将后一天的数据归零
        return result

    @staticmethod
    def total_base(data: list[int], days: int = 7) -> int:
        rng = len(data)
        day = DateTime().day - 1
        result = 0
        for _ in range(days):
            result += data[day]
            day = ((day-1+rng) % rng)
        return result

    def total_general(self, days: int = 7) -> int:
        data = self.update_general()
        return GroupActivity.total_base(data, days)

    def update_general(self, value_change: int = None) -> list[int]:
        return self.update_base('general', value_change)

    def total_command(self, days: int = 7) -> int:
        data = self.update_command()
        return GroupActivity.total_base(data, days)

    def update_command(self, value_change: int = None) -> list[int]:
        return self.update_base('command', value_change)
