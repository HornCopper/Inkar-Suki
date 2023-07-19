from ..jx3apiws import *
import time
import websockets

from typing import Optional
from websockets.legacy.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
import asyncio
from sgtpyutils.logger import logger
from src.tools.config import Config

import json


class SfWebSocket(object):
    connect: Optional[WebSocketClientProtocol] = None
    """ws链接"""

    def __new__(cls, *args, **kwargs):
        """单例"""
        if not hasattr(cls, "_instance"):
            orig = super(SfWebSocket, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

    async def ping(self):
        data = json.dumps({'action': 'ping', 'msg': '2333'}).encode('utf-8')
        await self.connect.send(data)

    async def ping_cycle(self):
        while True:
            await self.ping()
            await asyncio.sleep(10)

    async def _task(self):
        """
        说明:
            循环等待ws接受并分发任务
        """
        try:
            logger.debug(f'start msg recyle')
            asyncio.create_task(self.ping_cycle())
            while True:
                msg = await self.connect.recv()
                logger.debug(f'recv:{msg}')
                asyncio.create_task(self._handle_msg(msg))

        except ConnectionClosedOK:
            logger.debug("<g>sfapi > ws链接已主动关闭！</g>")

        except ConnectionClosedError as e:
            logger.error(f"<r>sfapi > ws链接异常关闭：{e.reason}</r>")
            # 自启动
            self.connect = None
            await self.init()
        except Exception as ex:
            logger.error(f'其他错误:{ex}')

        logger.debug('ws event loop exit')

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

    async def _handle_msg(self, message: bytes):
        """
        说明:
            处理收到的ws数据，分发给机器人
        """
        content = message.decode('utf-8')
        ws_client._handle_msg(content)

    async def init(self) -> Optional[bool]:
        """
        说明:
            初始化实例并连接ws服务器
        """
        if self.connect:
            return None

        ws_path = Config.sfapi_wslink
        ws_token = Config.sfapi_wstoken
        if ws_token is None:
            ws_token = ""
        headers = {"token": ws_token}
        logger.debug(f"<g>ws_server</g> | 正在链接sfapi的ws服务器：{ws_path}")
        for i in range(1, 101):
            try:
                logger.debug(f"<g>ws_server</g> | 正在开始第 {i} 次尝试")
                async with websockets.connect(
                    uri=ws_path,
                    extra_headers=headers,
                    ping_interval=5,
                    ping_timeout=5,
                    close_timeout=10,
                ) as websocket:
                    self.connect = websocket
                    logger.debug("<g>ws_server</g> | ws连接成功！")
                    await self._task()
                break
            except Exception as e:
                logger.error(f"<r>链接到ws服务器时发生错误：{str(e)}</r>")
                await asyncio.sleep(1)

        if not self.connect:
            # 未连接成功，发送消息给bot，如果有
            logger.warn("sfapi > ws服务器连接失败，请查看日志或者重连。")
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


sf_ws_client = None
if __name__ == '__main__':
    sf_ws_client = SfWebSocket()
    asyncio.run(sf_ws_client.init())
    while True:
        time.sleep(1)
else:
    sf_ws_client = SfWebSocket()
