from playwright.async_api import async_playwright
from pathlib import Path
from nonebot.log import logger

import pathlib2
import uuid
import os
import time

tools_path = f"{os.getcwd()}/src/tools"

def get_path(path: str) -> str:
    t = pathlib2.Path(tools_path)
    return t.parent.joinpath(path).__str__()

CACHE = get_path("cache")


def get_uuid():
    return str(uuid.uuid1()).replace("-", "")


async def generate_by_url(url: str, locate: str = None, first_element: bool = False, delay: int = 0, css: str = "", web: bool=False):
    try:
        async with async_playwright() as p:
            logger.opt(colors=True).info("<green>Generating source: " + url + "</green>")
            browser = await p.chromium.launch(headless=True, slow_mo=0)
            context = await browser.new_context()
            page = await context.new_page()
            if web:
                await page.goto(url)
            else:
                await page.goto({"path": url})
            if delay > 0:
                time.sleep(delay / 1000)
            uuid_ = get_uuid()
            store_path = f"{CACHE}/{uuid_}.png"
            await page.add_style_tag(content=css)
            if locate != None:
                if first_element:
                    await page.locator(locate).first.screenshot(path=store_path)
                else:
                    await page.locator(locate).screenshot(path=store_path)
            else:
                await page.screenshot(path=store_path)
            logger.opt(colors=True).info("<green>Generated successfully: " + store_path + "</green>")
            return store_path
    except Exception as ex:
        logger.info(f"音卡的图片生成失败啦！请尝试执行`playwright install`！:{ex}")
        return False


async def generate(path: str, web: bool = False, locate: str = None, first: bool = False, delay: int = 0, addtional_css: str = ""):
    """
    生成指定路径下html文件的截图
    @param path: HTML文件的本地路径或网络地址
    @param web: 是否为外网截图
    @param locate: 所截图的标签
    @param first: 是否只截图第一个元素
    @param delay: 等待时间，单位为毫秒（ms）
    @addtional_css: 追加的CSS
    """
    final_path = path
    result = await generate_by_url(final_path, locate, first, delay, addtional_css, web)
    if result is None:
        return False
    return result