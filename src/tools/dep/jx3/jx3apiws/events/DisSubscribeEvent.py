from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=10002)
class DisSubscribeEvent(RecvEvent):
    """取消订阅回执"""

    __event__ = "WsRecv.DisSubscribe"
    message_type = "DisSubscribe"
    action: Literal["烟花报时", "玄晶报时", "游戏消息"]
    """订阅内容"""
    server: list[str]
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
        log = f"取消订阅回执，类型：{self.action}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return f"[取消订阅回执]\n类型：{self.action}。"
