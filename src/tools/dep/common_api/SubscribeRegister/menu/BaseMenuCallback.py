from __future__ import annotations
from ..SubscribeItem import *
from ..events import *
from src.tools.dep.bot.group_env import *
from nonebot import get_driver


class BaseMenuCallback:
    lock: threading.Lock = threading.Lock()
    bots: list[Bot] = None

    def __init__(self, sub: SubscribeSubject, cron: SubjectCron) -> None:
        self.result = []
        self.sub = sub
        self.cron = cron
        with BaseMenuCallback.lock:
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
        '''bot group message from'''
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
            item = item if isinstance(item, tuple) else self.result[item]
            await self.send_msg_single(item)

    async def send_msg_single(self, item: tuple[str, str, str, str]):
        '''发送单条结果'''
        botname, group_id, to_send_msg, sub_from = item
        sub_name = sub_from.name if hasattr(sub_from, 'name') else sub_from
        to_send_msg = f'{to_send_msg}\n该消息来自[{sub_name}]订阅，如需退订回复 `退订 {sub_name}`'
        try:
            await BaseMenuCallback.bots.get(botname).call_api("send_group_msg", group_id=group_id, message=to_send_msg)
        except Exception as ex:
            logger.warning(f'{botname} bot fail to send msg -> {group_id}:{ex}')
