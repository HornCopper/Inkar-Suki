from playwright.async_api import async_playwright
from pathlib import Path
from nonebot.log import logger

import uuid
import time

from .basic import CACHE


def get_uuid():
    return str(uuid.uuid1()).replace("-", "")


async def generate_by_url(url: str, locate: str = None, first_element: bool = False, delay: int = 0):
    try:
        async with async_playwright() as p:
            logger.info("Generating source: " + url)
            browser = await p.chromium.launch(headless=True, slow_mo=0)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url)
            if delay > 0:
                time.sleep(delay / 1000)
            uuid_ = get_uuid()
            store_path = f"{CACHE}/{uuid_}.png"
            if locate != None:
                if first_element:
                    await page.locator(locate).first.screenshot(path=store_path)
                else:
                    await page.locator(locate).screenshot(path=store_path)
            else:
                await page.screenshot(path=store_path)
            logger.info("Generated successfully: " + store_path)
            return store_path
    except Exception as ex:
        logger.info(f"音卡的图片生成失败啦！请尝试执行`playwright install`！:{ex}")
        return False


async def generate(html: str, web: bool = False, locate: str = None, first: bool = False, delay: int = 0):
    """
    生成指定路径下html文件的截图
    @param html: HTML文件的本地路径
    @param web: 没什么用，填个`False`凑个数吧（已弃用的外网截图）
    @param locate: 所截图的标签
    @param first: 是否只截图第一个元素
    @param delay: 等待时间，单位为毫秒（ms）
    @return : 所生成的图片的本地路径
    """
    html = Path(html).as_uri()
    result = await generate_by_url(html, locate, first, delay)
    if result is None:
        return False
    return result