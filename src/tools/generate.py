from playwright.async_api import async_playwright
from pathlib import Path
from nonebot.log import logger

from src.tools.utils.path import CACHE

import uuid
import time

def get_uuid():
    return str(uuid.uuid1()).replace("-", "")


async def generate_by_url(url: str, locate: str = None, first_element: bool = False, delay: int = 0, css: str = "", web: bool=False, viewport: dict = {}, full_screen: bool = False):
    try:
        async with async_playwright() as p:
            logger.opt(colors=True).info("<green>Generating source: " + url + "</green>")
            browser = await p.chromium.launch(headless=True, slow_mo=0)
            if viewport == {}:
                context = await browser.new_context()
            else:
                context = await browser.new_context(
                    viewport=viewport
                )
            page = await context.new_page()
            await page.goto(url)
            if delay > 0:
                time.sleep(delay / 1000)
            uuid_ = get_uuid()
            store_path = f"{CACHE}/{uuid_}.png"
            if web:
                await page.add_style_tag(content=css)
            else:
                pass
            if locate != None:
                if first_element:
                        await page.locator(locate).first.screenshot(path=store_path)
                else:
                    await page.locator(locate).screenshot(path=store_path)
            else:
                await page.screenshot(path=store_path, full_page=full_screen)
            logger.opt(colors=True).info("<green>Generated successfully: " + store_path + "</green>")
            return store_path
    except Exception as ex:
        logger.info(f"音卡的图片生成失败啦！请尝试执行`playwright install`！:{ex}")
        return False


async def generate(
        path: str, 
        web: bool = False, 
        locate: str = None,
        first: bool = False, 
        delay: int = 0, 
        addtional_css: str = "", 
        viewport: dict = {}, 
        full_screen: bool = False
    ):
    """
    生成指定路径下html文件的截图
    @param path: HTML文件的本地路径或网络地址
    @param web: 是否为外网截图
    @param locate: 所截图的标签
    @param first: 是否只截图第一个元素
    @param delay: 等待时间，单位为毫秒（ms）
    @addtional_css: 追加的CSS
    """
    final_path = Path(path).as_uri() if not web else path
    result = await generate_by_url(final_path, locate, first, delay, addtional_css, web, viewport, full_screen)
    if result is None:
        return False
    return result