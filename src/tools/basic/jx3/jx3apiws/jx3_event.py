from .events import *
from .bot_event import *

import websockets
import asyncio

from typing import Optional

from websockets.legacy.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from src.tools.config import Config


class Jx3WebSocket:
    """
    jx3_api的ws链接封装
    """

    connect: Optional[WebSocketClientProtocol] = None
    """ws链接"""

    def __new__(cls, *args, **kwargs):
        """单例"""
        if not hasattr(cls, "_instance"):
            orig = super(Jx3WebSocket, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

    async def _task(self):
        """
        说明:
            循环等待ws接受并分发任务
        """
        try:
            while True:
                msg = await self.connect.recv()
                asyncio.create_task(BotEventController.handle_msg(msg))

        except ConnectionClosedOK:
            logger.debug("<g>jx3api > ws链接已主动关闭！</g>")
            await BotEventController.raise_notice("jx3api > ws已正常关闭！")

        except ConnectionClosedError as e:
            logger.error(f"<r>jx3api > ws链接异常关闭：{e.reason}</r>")
            # 自启动
            self.connect = None
            await self.init()

    async def init(self) -> Optional[bool]:
        """
        说明:
            初始化实例并连接ws服务器
        """
        if self.connect:
            return None

        ws_path = Config.jx3.ws.url
        ws_token = Config.jx3.ws.token
        if ws_token is None:
            ws_token = ""
        headers = {"token": ws_token}
        logger.debug(f"<g>ws_server</g> | 正在链接jx3api的ws服务器：{ws_path}")
        for i in range(1, 101):
            try:
                logger.debug(f"<g>ws_server</g> | 正在开始第 {i} 次尝试")
                self.connect = await websockets.connect(
                    uri=ws_path,
                    extra_headers=headers,
                    ping_interval=20,
                    ping_timeout=60,
                    close_timeout=60,
                )
                asyncio.create_task(self._task())
                logger.debug("<g>ws_server</g> | ws连接成功！")
                # await BotEventController.raise_notice("jx3api > ws已连接！")
                break
            except Exception as e:
                logger.error(f"<r>链接到ws服务器时发生错误：{str(e)}</r>")
                await asyncio.sleep(1)

        if not self.connect:
            # 未连接成功，发送消息给bot，如果有
            await BotEventController.raise_notice("jx3api > ws服务器连接失败，请查看日志或者重连。")
            return False
        return True

    async def close(self):
        """关闭ws链接"""
        if self.connect:
            await self.connect.close()
            self.connect = None

    @property
    def closed(self) -> bool:
        """ws是否关闭"""
        if self.connect:
            return self.connect.closed
        return True


ws_client = Jx3WebSocket()
