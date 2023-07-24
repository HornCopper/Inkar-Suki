import threading
import uuid
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from pathlib import Path
from nonebot.log import logger
import time
from src.tools.dep.bot.path import *

import asyncio


def get_uuid():
    return str(uuid.uuid1()).replace("-", "")


class PlaywrightThread(threading.Thread):
    def __init__(self) -> None:
        self.tasks: list[tuple[str, str, bool, int, asyncio.Future]] = []
        self.IsRunning = True
        self._player = None
        self.locker = threading.Lock()
        super().__init__(daemon=True)

    def init(self):
        player = sync_playwright().start()
        browser = player.chromium.launch(headless=True, slow_mo=0)
        page = browser.new_page()
        return page

    def stop(self):
        self.IsRunning = False

    def run(self) -> None:
        if self._player is None:
            self._player = self.init()
        while self.IsRunning:
            self.locker.acquire()
            if len(self.tasks) == 0:
                time.sleep(0.1)
                self.locker.release()
                continue
            task = self.tasks.pop()
            self.locker.release()
            url, locate, first, delay, future = task
            player = self._player
            try:
                player.goto(url)
                if delay > 0:
                    time.sleep(delay / 1000)
                uuid_ = get_uuid()
                img = f"{CACHE}/{uuid_}.png"
                if locate != None:
                    if first:
                        player.locator(locate).first.screenshot(path=img)
                    else:
                        player.locator(locate).screenshot(path=img)
                else:
                    player.screenshot(path=img)

                def callback(img: str):
                    future.set_result(img)
                future.get_loop().call_soon_threadsafe(callback, img)
            except Exception as ex:
                reason = f"音卡的图片[{url}]生成失败啦！请尝试执行`playwright install`！:{ex}"
                logger.warning(reason)
                future.set_exception(ex)
        return super().run()

    async def generate_by_url(self, url: str, locate: str = None, first: bool = False, delay: int = 0) -> str:
        future = asyncio.Future()
        self.locker.acquire()
        self.tasks.append([url, locate, first, delay, future])
        self.locker.release()
        result = await future
        return result


__client = PlaywrightThread()
__client.start()


def stop_playwright():
    __client.IsRunning = False


async def generate_by_url(url: str, locate: str = None, first: bool = False, delay: int = 0):
    result = await __client.generate_by_url(url, locate, first, delay)
    return result


async def generate(html: str, web: bool = False, locate: str = None, first: bool = False, delay: int = 0):
    '''
    生成指定路径下html文件的截图
    @param html: html文件路径
    @param web: 仅可填False，否则返回空
    @param locate: 填写指定标签以仅截图该标签
    @param first: 是否选取首个元素截图
    @param delay: 打开网页后延迟时间，单位ms
    @return : 返回生成的图片路径
    '''
    if web:
        pass
    html = Path(html).as_uri()
    result = await generate_by_url(html, locate, first, delay)
    if result is None:
        return False
    return result
