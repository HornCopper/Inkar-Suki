from __future__ import annotations
from src.tools.utils import *
from .CurrentGroupStatus import *
from .GroupActivity import *
from nonebot.adapters.onebot.v11 import Bot
from nonebot import get_driver


class GroupGather:
    cache_lock: threading.Lock = threading.Lock()
    group_cache: dict[str, CurrentGroupStatus] = filebase_database.Database(
        f'{bot_path.common_data_full}current-group-list',
        serializer=lambda data: dict([x, data[x].to_dict()] for x in data),
        deserializer=lambda data: dict([x, CurrentGroupStatus(data[x])] for x in data),
    ).value

    async def get_all_groups() -> dict[str, list[str]]:
        '''获取当前所有机器人所有群聊'''
        bots = get_driver().bots
        logger.debug(f'current online bots:{len(list(bots))}')

        tasks = {}
        for botname in bots:
            bot = bots.get(botname)
            group_ids = await GroupGather.get_groups(bot)
            for group in group_ids:
                tasks[group] = botname
        return tasks

    @staticmethod
    async def get_groups(bot: Bot):
        '''TODO migrate to group-statistics module'''
        with GroupGather.cache_lock:
            cache = GroupGather.group_cache.get(bot.self_id)
            if cache and not cache.is_outdated():
                result = cache.groups
                if result:  # 有数据才返回，否则重新加载
                    return result
            cache = CurrentGroupStatus()
            GroupGather.group_cache[bot.self_id] = cache
            group_list = []
            try:
                group_list = await bot.call_api("get_group_list")
            except Exception as ex:
                logger.warning(f'fail loading group of bot:{bot.self_id},{ex}')

            group_ids = [str(x.get("group_id")) for x in group_list]
            group_ids = extensions.distinct(group_ids)

            groups = [(x, GroupActivity(x).total_command()) for x in group_ids]
            groups = sorted(groups, key=lambda grp: grp[1], reverse=True)  # 按活跃度降序
            cache.groups = [x[0] for x in groups]
            return cache.groups
