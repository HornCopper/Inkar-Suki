import uuid
from playwright.async_api import async_playwright
from pathlib import Path
from nonebot.log import logger
import time
from src.tools.dep.bot.path import *

def get_uuid():
    return str(uuid.uuid1()).replace("-", "")


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
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, slow_mo=0)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(html)
            if delay > 0:
                time.sleep(delay / 1000)
            uuid_ = get_uuid()
            img = f"{CACHE}/{uuid_}.png"
            if locate != None:
                if first:
                    await page.locator(locate).first.screenshot(path=img)
                else:
                    await page.locator(locate).screenshot(path=img)
            else:
                await page.screenshot(path=img)
            return img
    except Exception as ex:
        logger.info(f"音卡的图片生成失败啦！请尝试执行`playwright install`！:{ex}")
        return False
