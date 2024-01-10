import os
import copy
from sgtpyutils.database import filebase_database
from src.tools.utils import *

from .GroupConfigPreset import *
config_dict = {
    'jx3group': groupConfigInfos,
    'jx3user': userConfigInfos
}


class GroupConfig:
    def get_db_path(self) -> str:
        return bot_path.get_group_config(self.group_id, self.config)

    def __init__(self, group_id: str, config: str = 'jx3group', config_root: dict[str, GroupConfigInfo] = None) -> None:
        self.group_id = str(group_id)
        self.config = config
        self.root = config_root if config_root else config_dict.get(config)
        p: str = self.get_db_path()
        self._db = filebase_database.Database(p)
        self.value = self._db.value

    def mgr_property(self, keys: list[str], new_val: any = Ellipsis) -> any:
        if isinstance(keys, str):
            keys = keys.split('.')  # 转为属性组
        action = 'fetch' if new_val is Ellipsis else f'= {new_val}'
        data = self.value
        result = self.enter_property(data, self.root, keys, new_val)
        logger.debug(
            f'mgr_property@{self.group_id}:{self.config} {str.join(".",keys)} {action},result={result}')
        return result

    def enter_property(self, data: dict, option: dict[str, GroupConfigInfo], keys: list[str], new_val: any = Ellipsis):
        cur = keys[0]
        keys = keys[1:]

        assert cur in option, f'配置项{cur}不存在'
        cur_opt = option.get(cur)

        cur_data = data.get(cur)
        if cur_data is None:
            cur_data = copy.deepcopy(cur_opt.default)

        if len(keys):
            assert cur_data is not None, 'data无下一级属性'
            assert isinstance(cur_data, dict), 'data非属性集合'
            next_options = cur_opt.infos
            assert next_options is not None, 'options无下一级属性'
            assert isinstance(next_options, dict), 'options非属性集合'
            return self.enter_property(cur_data, next_options, keys, new_val)

        if new_val is not Ellipsis:
            # 更新属性
            data[cur] = new_val
        return cur_data


class GroupUserConfig(GroupConfig):
    def get_db_path(self) -> str:
        return bot_path.get_user_config(self.group_id, self.config)

    def __init__(self, group_id: str, config: str = 'jx3user', config_root: dict[str, GroupConfigInfo] = None) -> None:
        super().__init__(group_id, config, config_root)
