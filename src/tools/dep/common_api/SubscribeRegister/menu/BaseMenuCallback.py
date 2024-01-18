from __future__ import annotations
from ..SubscribeItem import *
from .CurrentGroupStatus import *
from ..events import *
from src.tools.dep.bot.group_env import *
from nonebot import get_driver


async def OnCallback(sub: SubscribeSubject, cron: SubjectCron):
    return await BaseMenuCallback(sub, cron).run()


class BaseMenuCallback:
    group_cache: dict[str, CurrentGroupStatus] = filebase_database.Database(
        f'{bot_path.common_data_full}current-group-list',
        serializer=lambda data: dict([x, data[x].to_dict()] for x in data),
        deserializer=lambda data: dict([x, CurrentGroupStatus(data[x])] for x in data),
    ).value
    cache_lock: threading.RLock = threading.RLock()

    @classmethod
    def from_general_name(cls, subject_name: str, cron_level: int = 0, description: str = '事件订阅', log_name: str = '通用事件') -> BaseMenuCallback:
        target = BaseMenuCallback(
            sub=SubscribeSubject(
                name=subject_name,
                description=description,
            ),
            cron=SubjectCron(
                exp='',
                notify=log_name
            )
        )
        target.result = ext.SyncRunner.as_sync_method(BaseMenuCallback.get_all_group_of_subscribe(
            subject=subject_name,
            cron_level=cron_level,  # 通用事件默认级别为0
        ))
        return target

    def __init__(self, sub: SubscribeSubject, cron: SubjectCron) -> None:
        self.result = []
        self.sub = sub
        self.cron = cron

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
        await self.init_messages()
        return await self.start_send_msg()

    async def start_send_msg(self):
        '''将收集到的结果发送出去'''
        logger.info(f'start send subscribe...{self.statistics}')
        for item in self.valid_result:
            await self.send_msg_single(item)

    async def send_msg_single(self, item):
        '''发送单条结果'''
        botname, group_id, to_send_msg, sub_from = item
        sub_name = sub_from.name if hasattr(sub_from, 'name') else sub_from
        to_send_msg = f'{to_send_msg}\n该消息来自[{sub_name}]订阅，如需退订回复 `退订 {sub_name}`'
        try:
            await self.bots.get(botname).call_api("send_group_msg", group_id=group_id, message=to_send_msg)
        except Exception as ex:
            logger.warning(f'{botname} bot fail to send msg -> {group_id}:{ex}')

    @staticmethod
    async def get_groups(bot: Bot):
        with BaseMenuCallback.cache_lock:
            cache = BaseMenuCallback.group_cache.get(bot.self_id)
            if cache and not cache.is_outdated():
                return cache.groups
        cache = CurrentGroupStatus()
        BaseMenuCallback.group_cache[bot.self_id] = cache
        group_list = await bot.call_api("get_group_list")
        group_ids = [str(x.get("group_id")) for x in group_list]
        group_ids = extensions.distinct(group_ids)

        groups = [(x, GroupActivity(x).total_command()) for x in group_ids]
        groups = sorted(groups, key=lambda grp: grp[1], reverse=True)  # 按活跃度降序
        cache.groups = [x[0] for x in group_ids]
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

    @staticmethod
    async def get_all_group_of_subscribe(subject: str, cron_level: int) -> dict[str, tuple[str, str, str]]:
        '''获取指定主题已订阅的群
        @return
            dict[str,tuple[str,str,str]] key:(机器人id 群号 是否应发 订阅来源)
        '''
        tasks = await BaseMenuCallback.get_all_groups()
        result = {}
        for group_id in tasks:
            botname = tasks[group_id]
            key = f'{botname}@{group_id}'
            if key in result:
                logger.warning(f'subscribe:message-to-send already in {key}')

            g_subscribe = GroupConfig(group_id, log=False).mgr_property('subscribe')
            u_subscribed_level, sub_from = BaseMenuCallback.check_subscribed(subject, g_subscribe)
            to_send_msg = u_subscribed_level >= cron_level
            result[key] = (botname, group_id, to_send_msg, sub_from)
        return result

    async def init_messages(self):
        '''收集各群的订阅结果'''
        result = await BaseMenuCallback.get_all_group_of_subscribe(self.sub, self.cron.level)

        for key in result:
            botname, group_id, to_send_msg, sub_from = result[key]
            while to_send_msg:
                callback_result = await self.callback(group_id, self.sub, self.cron)
                # 如果有返回值则表示需要发送
                if not callback_result or not isinstance(callback_result, str):
                    to_send_msg = None
                    break
                to_send_msg = callback_result
                break

            result[key] = (botname, group_id, to_send_msg, sub_from)

        self.result = [result[x] for x in result]
