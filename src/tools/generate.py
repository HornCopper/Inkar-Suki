from playwright.async_api import async_playwright
from pathlib import Path

from nonebot.log import logger
from src.tools.utils.path import CACHE

import uuid
import asyncio
import time

def get_uuid():
    return str(uuid.uuid1()).replace("-", "")


async def generate(
    path: str,
    web: bool = False,
    locate: str = None,
    first: bool = False,
    delay: int = 0,
    additional_css: str = "",
    viewport: dict = None,
    full_screen: bool = False
):
    """
    生成指定路径下html文件的截图
    @param path: HTML文件的本地路径或网络地址
    @param web: 是否为外网截图
    @param locate: 所截图的标签
    @param first: 是否只截图第一个元素
    @param delay: 等待时间，单位为毫秒（ms）
    @param additional_css: 追加的CSS
    @param viewport: 浏览器视口设置
    @param full_screen: 是否截图整个页面
    """
    if viewport is None:
        viewport = {}

    final_path = Path(path).as_uri() if not web else path

    try:
        async with async_playwright() as p:
            time_start = time.time()
            logger.opt(colors=True).info(f"<green>Generating source: {final_path}</green>")
            browser = await p.chromium.launch(headless=True, slow_mo=0)
            context = await browser.new_context(viewport=viewport if viewport else None)
            page = await context.new_page()
            await page.goto(final_path)
            if delay > 0:
                await asyncio.sleep(delay / 1000)

            uuid_ = get_uuid()
            store_path = f"{CACHE}/{uuid_}.png"

            if web:
                await page.add_style_tag(content=additional_css)

            if locate:
                locator = page.locator(locate).first if first else page.locator(locate)
                await locator.screenshot(path=store_path)
            else:
                await page.screenshot(path=store_path, full_page=full_screen)

            time_end = time.time()
            logger.opt(colors=True).info(f"<green>Generated successfully: {store_path}, spent {round(time_end - time_start, 2)}s</green>")
            return store_path
    except Exception as ex:
        logger.info(f"音卡的图片生成失败啦！请尝试执行`playwright install`！: {ex}")
        return False
