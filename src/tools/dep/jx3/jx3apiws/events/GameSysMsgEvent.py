from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1008)
class GameSysMsgEvent(RecvEvent):
    """游戏系统频道消息推送"""

    __event__ = "WsRecv.GameSysMsg"
    message_type = "GameSysMsg"
    message: str
    """消息内容"""
    time: str
    """消息时间"""

    @property
    def log(self) -> str:
        log = f"系统频道推送：{self.message}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return f"[系统频道推送]\n时间：{self.time}\n{self.message}。"
