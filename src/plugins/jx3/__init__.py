from nonebot import get_driver, logger

from src.tools.config import Config

from .jx3 import *

import asyncio
import websockets

driver = get_driver()

async def websocket_client(ws_url: str, headers: dict):
    while True:
        try:
            async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                logger.info("WebSocket connection established")
                while True:
                    response = await websocket.recv()
                    logger.info(f"Received: {response}")
                    await asyncio.sleep(1)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed, retrying...")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        await asyncio.sleep(2)

@driver.on_startup
async def on_startup():
    ws_url = Config.jx3.ws.url
    headers = {
        "token": Config.jx3.ws.token
    }
    asyncio.create_task(websocket_client(ws_url, headers))
