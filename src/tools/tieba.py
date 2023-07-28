import random
import asyncio
import aiotieba
from typing import List
import threading
import time

from sgtpyutils.logger import logger
from sgtpyutils.extensions import distinct


class SubjectStatus:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.last_thread_index: int = 0  # 上次已获取到的帖子序号
        self.last_fetch: int = 0  # 上次加载时间
        self._threads = []  # 存储的

    @property
    def threads(self):
        return self._threads

    @threads.setter
    def threads(self, v: list):
        self._threads = distinct(v, lambda x: x.tid)


class Jx3Tieba(threading.Thread):
    Interval = 3  # 延迟
    Interval_Rnd = 1  # 随机变换
    name = "tieba thread"  # 线程名称

    def __init__(self, subject: List[str]) -> None:
        self.subject = subject or ["剑网三"]
        v = "|".join(subject)
        logger.info(f"{Jx3Tieba.name} load subjects:{v}")
        self.subject_status = {}
        self._current_index = 0
        self.is_stop = True
        super().__init__(name=Jx3Tieba.name, daemon=True)

    def start(self) -> None:
        logger.info(f"{self.name} is going to start")
        if not self.is_stop:
            return
        self.is_stop = False
        return super().start()

    def stop(self):
        logger.info(f"{self.name} is going to stop")
        self.is_stop = True

    @staticmethod
    def get_interval() -> float:
        s = Jx3Tieba.Interval * 1000
        r = Jx3Tieba.Interval_Rnd * 1000
        return random.randint(s-r, s+r) / 1000

    @property
    def current_index(self) -> int:
        return self._current_index

    @current_index.setter
    def current_index(self, v: int):
        if v >= len(self.subject):
            v = 0
        self._current_index = v

    @property
    def current_subject(self) -> str:
        return self.subject[self.current_index]

    @property
    def current_status(self) -> SubjectStatus:
        if not self.current_subject in self.subject_status:
            self.subject_status[self.current_subject] = SubjectStatus(
                self.current_subject)
        return self.subject_status[self.current_subject]

    def run(self):
        logger.debug(f"{self.name} proceeding.")
        while True:
            self.current_index += 1
            asyncio.run(self.run_once())
            if self.is_stop:
                return logger.info(f"{self.name} is stopped")
            time.sleep(Jx3Tieba.get_interval())

    async def run_once(self) -> list:
        if not self.is_alive():
            self.stop()
            return []
        return await self.__run_once()

    async def __run_once(self):
        s: SubjectStatus = self.current_status
        s.last_fetch = time.time()
        pn = 1
        while True:
            async with aiotieba.Client() as client:
                sub = self.current_subject
                logger.debug(f"{self.name}:load forum[{sub}] at page {pn}")
                _threads = await client.get_threads(sub, pn=pn)
                t_index = _threads.page.total_page * _threads.page.page_size - pn
                s.threads += _threads[0:]
                logger.debug(
                    f"{self.name}:load forum[{sub}] at page {pn}, loaded threads:{len(s.threads)}")
                if s.last_thread_index == 0:
                    s.last_thread_index = t_index
                    break
                if t_index <= s.last_thread_index:
                    break
                pn += 1
                time.sleep(Jx3Tieba.get_interval())
        return s.threads


client = Jx3Tieba(["唯满侠", "剑网三", "剑三", "剑网三交易", "剑网三外观"])
client.start()
