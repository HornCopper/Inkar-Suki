from playwright.async_api import async_playwright
from datetime import datetime, timedelta

from nonebot.log import logger

from src.utils.database.operation import send_subscribe

import asyncio

def trim_to_last_period(s: str) -> str:
    return s[:s.rfind("。") + 1] if "。" in s else s

def check_time(timestamp: str) -> bool:
    given_time = datetime.strptime(timestamp, "%a %b %d %H:%M:%S %z %Y")
    now = datetime.now(given_time.tzinfo)
    time_difference = now - given_time
    return time_difference > timedelta(hours=2)

async def execute_on_new_post(post):
    data = trim_to_last_period(post.get("text_raw"))
    logger.info({"data": data})
    await send_subscribe("咸鱼", data)

async def poll_weibo_api(uid, interval=60):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        logger.info("Start successfully!")
        last_seen_id = None
        while True:
            logger.info("Running application.")
            try:
                await page.goto("https://weibo.com")
                await page.wait_for_timeout(5000)
                response = await page.goto(f"https://weibo.com/ajax/statuses/mymblog?uid={uid}")
                data = await response.json() # type: ignore
                if "data" in data and "list" in data["data"]:
                    posts = data["data"]["list"]
                    if posts:
                        latest_post = posts[0]
                        post_id = latest_post.get("idstr")
                        
                        if last_seen_id != post_id and not check_time(latest_post.get("created_at")):
                            await execute_on_new_post(latest_post)
                            last_seen_id = post_id
                        
                        logger.info(f"Request completed! {last_seen_id}")
                    else:
                        logger.info("No new information!")
                else:
                    logger.info("No data!")
                    
            except Exception as e:
                logger.info("Request failed!")
            
            await asyncio.sleep(interval)