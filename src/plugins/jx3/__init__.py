from nonebot import get_driver, logger

from src.tools.config import Config

from .jx3 import *
from .parse import *

import asyncio
import websockets
import json

driver = get_driver()

async def websocket_client(ws_url: str, headers: dict):
    while True:
        try:
            async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                logger.info("WebSocket connection established")
                while True:
                    response = await websocket.recv()
                    raw_response = response
                    response = json.loads(response)
                    if response["action"] not in get_registered_actions():
                        logger.warning("未知JX3API 消息: " + raw_response)
                        continue
                    logger.info("JX3API 解析成功: " + raw_response)
                    parsed = parse_data(response)
                    msg: JX3APIOutputMsg = parsed.msg()
                    await send_subscribe(msg.name, msg.msg, msg.server)
                    logger.info(msg.msg)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed, retrying...")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")

@driver.on_startup
async def on_startup():
    ws_url = Config.jx3.ws.url
    headers = {
        "token": Config.jx3.ws.token
    }
    asyncio.create_task(websocket_client(ws_url, headers))