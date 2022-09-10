import websockets
import asyncio
import json
import nonebot
import sys

from typing import Optional

from websockets.legacy.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from nonebot.log import logger

from nonebot import get_bots
from nonebot.message import handle_event

from .jx3_event import EventRister, WsData, WsNotice

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
from config import Config

class Jx3WebSocket(object):
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
                asyncio.create_task(self._handle_msg(msg))

        except ConnectionClosedOK:
            logger.debug("<g>jx3api > ws链接已主动关闭！</g>")
            await self._raise_notice("jx3api > ws已正常关闭！")

        except ConnectionClosedError as e:
            logger.error(f"<r>jx3api > ws链接异常关闭：{e.reason}</r>")
            # 自启动
            self.connect = None
            await self.init()

    async def _raise_notice(self, message: str):
        """
        说明:
            抛出ws通知事件给机器人
        参数:
            * `message`：通知内容
        """
        event = WsNotice(message=message)
        bots = get_bots()
        for _, one_bot in bots.items():
            await handle_event(one_bot, event)

    async def _handle_msg(self, message: str):
        """
        说明:
            处理收到的ws数据，分发给机器人
        """
        try:
            ws_obj = json.loads(message)
            data = WsData.parse_obj(ws_obj)
            event = EventRister.get_event(data)
            if event:
                logger.debug(event.log)
                bots = get_bots()
                for _, one_bot in bots.items():
                    await handle_event(one_bot, event)
            else:
                logger.error(f"<r>未知的ws消息类型：{data}</r>")
        except Exception:
            logger.error(f"未知ws消息：<g>{ws_obj}</g>")

    async def init(self) -> Optional[bool]:
        """
        说明:
            初始化实例并连接ws服务器
        """
        if self.connect:
            return None

        ws_path = Config.jx3api_wslink
        ws_token = Config.jx3api_wstoken
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
                    ping_timeout=20,
                    close_timeout=10,
                )
                asyncio.create_task(self._task())
                logger.debug("<g>ws_server</g> | ws连接成功！")
                # await self._raise_notice("jx3api > ws已连接！")
                break
            except Exception as e:
                logger.error(f"<r>链接到ws服务器时发生错误：{str(e)}</r>")
                asyncio.sleep(1)

        if not self.connect:
            # 未连接成功，发送消息给bot，如果有
            await self._raise_notice("jx3api > ws服务器连接失败，请查看日志或者重连。")
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