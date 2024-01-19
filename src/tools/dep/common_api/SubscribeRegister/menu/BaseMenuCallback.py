from __future__ import annotations
from ..SubscribeItem import *
from .CurrentGroupStatus import *
from ..events import *
from src.tools.dep.bot.group_env import *
from nonebot import get_driver


class BaseMenuCallback:
    group_cache: dict[str, CurrentGroupStatus] = filebase_database.Database(
        f'{bot_path.common_data_full}current-group-list',
        serializer=lambda data: dict([x, data[x].to_dict()] for x in data),
        deserializer=lambda data: dict([x, CurrentGroupStatus(data[x])] for x in data),
    ).value
    cache_lock: threading.Lock = threading.Lock()
    bots: list[Bot] = None


    def __init__(self, sub: SubscribeSubject, cron: SubjectCron) -> None:
        self.result = []
        self.sub = sub
        self.cron = cron
        with BaseMenuCallback.cache_lock:
            if not BaseMenuCallback.bots:
                BaseMenuCallback.bots = get_driver().bots

    @property
    def callback(self):
        # 回调获取应发消息
        func = self.sub.callback if self.sub.callback else OnDefaultCallback
        return func

    @property
    def valid_result(self):
        result = self.result
        return [x for x in result if x[2]]

    @property
    def statistics(self):
        total = len(self.result)
        valid = len(self.valid_result)
        pre = f"events:{self.sub.name}[{self.cron.notify_content}] to "
        statistics = f"{valid}/{total} groups"
        return f'{pre}{statistics}'

    async def run(self):
        return await self.start_send_msg()

    async def start_send_msg(self):
        '''将收集到的结果发送出去'''
        logger.info(f'start send subscribe...{self.statistics}')
        BaseMenuCallback.bots = get_driver().bots
        for item in self.valid_result:
            await self.send_msg_single(item)

    async def send_msg_single(self, item):
        '''发送单条结果'''
        botname, group_id, to_send_msg, sub_from = item
        sub_name = sub_from.name if hasattr(sub_from, 'name') else sub_from
        to_send_msg = f'{to_send_msg}\n该消息来自[{sub_name}]订阅，如需退订回复 `退订 {sub_name}`'
        try:
            await BaseMenuCallback.bots.get(botname).call_api("send_group_msg", group_id=group_id, message=to_send_msg)
        except Exception as ex:
            logger.warning(f'{botname} bot fail to send msg -> {group_id}:{ex}')

    @staticmethod
    async def get_groups(bot: Bot):
        '''TODO migrate to group-statistics module'''
        with BaseMenuCallback.cache_lock:
            cache = BaseMenuCallback.group_cache.get(bot.self_id)
            if cache and not cache.is_outdated():
                result = cache.groups
                if result:  # 有数据才返回，否则重新加载
                    return result
            cache = CurrentGroupStatus()
            BaseMenuCallback.group_cache[bot.self_id] = cache
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

    async def get_all_groups() -> dict[str, list[str]]:
        '''获取当前所有机器人所有群聊'''
        bots = get_driver().bots
        logger.debug(f'current online bots:{len(list(bots))}')

        tasks = {}
        for botname in bots:
            bot = bots.get(botname)
            group_ids = await BaseMenuCallback.get_groups(bot)
            for group in group_ids:
                tasks[group] = botname
        return tasks
