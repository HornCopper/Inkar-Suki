from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=10001)
class SubscribeEvent(RecvEvent):
    """订阅回执"""

    __event__ = "WsRecv.Subscribe"
    message_type = "Subscribe"
    action: Literal["烟花报时", "玄晶报时", "游戏消息"]
    """订阅内容"""
    server: list
    """已订阅服务器"""

    @validator("action", pre=True)
    def check_action(cls, v):
        if v == 1006:
            return "烟花报时"
        elif v == 1007:
            return "玄晶报时"
        elif v == 1010:
            return "游戏消息"

    @property
    def log(self) -> str:
        log = f"订阅回执，类型：{self.action}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return f"[订阅回执]\n类型：{self.action}。"
