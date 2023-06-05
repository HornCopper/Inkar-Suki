import uuid
from playwright.async_api import async_playwright
import sys
import nonebot
from pathlib import Path
from nonebot.log import logger
TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
CACHE = TOOLS.replace("tools","cache")

def get_uuid():
    return str(uuid.uuid1()).replace("-","")

async def generate(html: str, web: bool, locate: str = None, first: bool = False):
    if web:
        pass
    html = Path(html).as_uri()
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless = True, slow_mo = 0)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(html)
            uuid_ = get_uuid()
            img = CACHE + "/" + uuid_ + ".png"
            if locate != None:
                if first:
                    await page.locator(locate).first.screenshot(path = img)
                else:
                    await page.locator(locate).screenshot(path = img)
            else:
                await page.screenshot(path = img)
            return img
    except Exception as ex:
        logger.info(f"音卡的图片生成失败啦！请尝试执行`playwright install`！:{ex}")
