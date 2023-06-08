import random
import asyncio
import aiotieba
from typing import List
import threading
import time

from sgtpyutils.logger import logger
class SubjectStatus:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.last_thread_index: int = 0  # 上次已获取到的帖子序号


class Jx3Tieba:
    Interval = 3  # 延迟
    Interval_Rnd = 1  # 随机变换

    def __init__(self, subject: List[str]) -> None:
        self.subject = subject
        self.subject_status = {}
        self.current_index = 0

    @staticmethod
    def get_interval() -> float:
        s = Jx3Tieba.Interval * 1000
        r = Jx3Tieba.Interval_Rnd * 1000
        return random.randint(s-r, s+r) / 1000

    @property
    def current_subject(self) -> str:
        return self.subject[self.current_index]

    @property
    def current_status(self) -> SubjectStatus:
        if not self.current_subject in self.subject_status:
            self.subject_status[self.current_subject] = SubjectStatus(
                self.current_subject)
        return self.subject_status[self.current_subject]

    async def run_once(self) -> list:
        threads = []
        s: SubjectStatus = self.current_status
        pn = 0
        while True:
            async with aiotieba.Client() as client:
                sub = self.current_subject
                logger.debug(f'load forum[{sub}] at page {pn}')
                _threads = await client.get_threads(sub, pn=pn)
                t_index = _threads.page.total_page * _threads.page.page_size - pn
                threads += [_threads[0:]]
                if s.last_thread_index == 0:
                    s.last_thread_index = t_index
                    break
                if t_index <= s.last_thread_index:
                    break
                pn += 1
                time.sleep(Jx3Tieba.get_interval())
        return threads

client = Jx3Tieba(['唯满侠', '剑网三'])
