from playwright.async_api import Browser
from nonebot import get_driver
from nonebot.log import logger

from src.config import Config
from src.const.path import ASSETS, build_path
from src.utils.generate import (
    ScreenshotGenerator,
    generate
)
from src.utils.time import Time
from src.utils.database import cache_db
from src.utils.database.classes import JX3APIWSData
from src.utils.database.operation import send_subscribe

from .parse import (
    get_registered_actions,
    parse_data,
    JX3APIOutputMsg
)
from .weibo import poll_weibo_api

from .universe import * # 要不你来一个一个导？

import re
import shutil
import asyncio
import websockets
import json
import os

driver = get_driver()

async def websocket_client(ws_url: str, headers: dict):
    while True:
        try:
            async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                logger.info("WebSocket connection established")
                while True:
                    response_text = await websocket.recv()
                    raw_response = response_text
                    response: dict = json.loads(response_text)
                    if response["action"] not in get_registered_actions():
                        logger.warning("未知JX3API 消息: " + str(raw_response))
                        continue
                    logger.info("JX3API 解析成功: " + str(raw_response))
                    parsed = parse_data(response)
                    msg: JX3APIOutputMsg = parsed.msg()
                    cache_db.save(
                        JX3APIWSData(
                            action = response["action"],
                            event = msg.name,
                            data = response["data"],
                            timestamp = Time().raw_time
                        )
                    )
                    name = msg.name
                    if name == "公告":
                        url, title = parsed.provide_data()
                        if re.match(r"(\d+)月(\d+)日(.*?)版本更新公告", title):
                            if os.path.exists(build_path(ASSETS, ["image", "jx3", "update.png"])):
                                os.remove(build_path(ASSETS, ["image", "jx3", "update.png"]))
                            await generate(
                                url, 
                                ".allnews_list_container", 
                                True,
                                viewport={"height": 3840, "width": 2000}, 
                                hide_classes=["detail_bot", "bdshare-slide-button"], 
                                device_scale_factor=2.0,
                                output_path=build_path(ASSETS, ["image", "jx3", "update.png"])
                            )
                    await send_subscribe(name, msg.msg, msg.server)
                    logger.info(msg.msg)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed, retrying...")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        await asyncio.sleep(3)

@driver.on_startup
async def on_startup():
    ws_url = Config.jx3.ws.url
    headers = {
        "token": Config.jx3.ws.token
    }
    asyncio.create_task(websocket_client(ws_url, headers))
    asyncio.create_task(ScreenshotGenerator.launch())
    if Config.jx3.api.weibo:
        asyncio.create_task(poll_weibo_api("2046281757", interval=600))