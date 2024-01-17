from __future__ import annotations
from .SubscribeItem import *
from .events import *
from src.tools.dep.bot.group_env import *
from nonebot import get_driver
# 订阅 主题 订阅等级
__subjects: list[SubscribeSubject] = []
VALID_Subjects: dict[str, SubscribeSubject] = {}


def load_subjects(__subjects: list[SubscribeSubject], target: dict[str, SubscribeSubject]):
    """
    从预设逻辑中初始化
    @param __subjects 初始化主题到列表
    @param target 初始化主题到字典
    """
    init_subjects(__subjects)
    logger.info(f"subscribes inited: count {len(__subjects)}")
    for sub in __subjects:
        target[sub.name] = sub
        init_cron(sub, OnCallback)


def get_subscribe_items(user_subs: dict[str, dict]):
    """
    将当前订阅转换为实体
    """
    r = []
    for x in user_subs:
        v = VALID_Subjects.get(x)
        if not v:
            continue
        v.set_user_args(user_subs.get(x))
        r.append(v)
    return r


async def OnCallback(sub: SubscribeSubject, cron: SubjectCron):
    return await MenuCallback(sub, cron).run()


class MenuCallback:

    @staticmethod
    def check_subscribed(target_subject: SubscribeSubject, user_subs: dict[str, dict], sub_from: SubscribeSubject = None) -> tuple[bool, SubscribeSubject]:
        """
        检查当前订阅是否已包含
        @return tuple[
            当前监听参数值，-1表示未监听
            订阅的来源
        ]
        """
        if isinstance(target_subject, SubscribeSubject):
            target_subject = target_subject.name

        def get_user_arg(v):
            return get_number(v.get("arg"))
        v = user_subs.get(target_subject)
        if v is not None:  # 数值
            return get_user_arg(v), sub_from or target_subject

        result = -1
        for s in user_subs:
            u_sub = VALID_Subjects.get(s)  # 获取当前项
            if u_sub is None:
                continue
            cur_value = user_subs.get(s) or {}
            # 子项继承父项的事件等级
            children_value = dict([[x, cur_value] for x in u_sub.children])
            # 逐个检查子项，并选择其中监听等级最高的返回，默认返回-1
            sub_level, _ = MenuCallback.check_subscribed(
                target_subject, children_value, sub_from)
            if not isinstance(sub_level, int):
                sub_level = get_user_arg(sub_level)
            if result < sub_level:
                result = sub_level
                sub_from = u_sub
        return result, sub_from

    @classmethod
    def from_general_name(cls, subject_name: str, cron_level: int = 0, description: str = '事件订阅', log_name: str = '通用事件') -> MenuCallback:
        target = MenuCallback(
            sub=SubscribeSubject(
                name=subject_name,
                description=description,
            ),
            cron=SubjectCron(
                exp='',
                notify=log_name
            )
        )
        target.result = ext.SyncRunner.as_sync_method(MenuCallback.get_all_group_of_subscribe(
            subject=subject_name,
            cron_level=cron_level,  # 通用事件默认级别为0
        ))
        return target

    def __init__(self, sub: SubscribeSubject, cron: SubjectCron) -> None:
        self.result = []
        self.bots = get_driver().bots
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
    async def get_all_group_of_subscribe(subject: str, cron_level: int) -> dict[str, tuple[str, str, str]]:
        '''获取指定主题已订阅的群
        @return
            dict[str,tuple[str,str,str]] key:(机器人id 群号 是否应发 订阅来源)
        '''
        bots = get_driver().bots
        logger.debug(f'current online bots:{len(list(bots))}')
        result = {}

        tasks = {}
        for botname in bots:
            bot = bots.get(botname)
            group_ids = [str(x.get("group_id")) for x in await bot.call_api("get_group_list")]
            group_ids = extensions.distinct(group_ids)
            for group in group_ids:
                tasks[group] = botname

        for group_id in tasks:
            botname = tasks[group_id]
            key = f'{botname}@{group_id}'
            if key in result:
                logger.warning(f'subscribe:message-to-send already in {key}')

            g_subscribe = GroupConfig(group_id, log=False).mgr_property('subscribe')
            u_subscribed_level, sub_from = MenuCallback.check_subscribed(subject, g_subscribe)
            to_send_msg = u_subscribed_level >= cron_level
            result[key] = (botname, group_id, to_send_msg, sub_from)
        return result

    async def init_messages(self):
        '''收集各群的订阅结果'''
        result = await MenuCallback.get_all_group_of_subscribe(self.sub, self.cron.level)

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


load_subjects(__subjects, VALID_Subjects)
