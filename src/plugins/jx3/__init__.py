from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment

from src.config import Config
from src.utils.time import Time
from src.utils.database import cache_db
from src.utils.database.classes import JX3APIWSData
from src.utils.database.operation import send_subscribe
from src.utils.network import Request
from src.plugins.jx3.announce.image import get_beta_push_image, get_push_image
from src.plugins.jx3.weibo import get_weibo_push_image

from .parse import (
    get_registered_actions,
    parse_data,
    JX3APIOutputMsg
)
from .universe import * # 要不你来一个一个导？  # noqa: F403

import asyncio
import websockets
import json

driver = get_driver()

async def websocket_client(ws_url: str, headers: dict):
    if not Config.jx3.ws.enable:
        return
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
                            data = response["detail"],
                            timestamp = Time().raw_time
                        )
                    )
                    name = msg.name
                    message = msg.msg
                    server = msg.server
                    if name == "公告":
                        url, _ = parsed.provide_data()
                        try:
                            message = msg.msg + await get_push_image(url)
                        except Exception:
                            logger.exception(f"生成官网公告截图失败，继续发送文字公告：{url}")
                    if name == "体服公告":
                        try:
                            message = msg.msg + await get_beta_push_image()
                        except Exception:
                            logger.exception("生成体服公告截图失败，继续发送文字公告")
                    if name == "咸鱼":
                        post_id, _ = parsed.provide_data()
                        try:
                            message = msg.msg + await get_weibo_push_image(post_id)
                        except Exception:
                            logger.exception(
                                f"生成微博卡片截图失败，继续发送文字：{post_id}"
                            )
                    if name in ["生日祝福", "创作者"]:
                        image = (await Request(server).get()).content
                        message = msg.msg + MessageSegment.image(image)
                        server = ""
                    await send_subscribe(name, message, server)
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
