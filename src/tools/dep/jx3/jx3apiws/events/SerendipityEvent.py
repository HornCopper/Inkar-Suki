from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1001)
class SerendipityEvent(RecvEvent):
    """奇遇播报事件"""

    __event__ = "WsRecv.Serendipity"
    message_type = "Serendipity"
    name: str
    """触发角色"""
    serendipity: str
    """奇遇名"""
    level: int
    """奇遇等级"""
    time: str
    """触发时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        return DateTime(int(v)).tostring("%m/%d %H:%M")

    @property
    def log(self) -> str:
        log = f"奇遇推送事件：[{self.server}]的[{self.name}]抱走了奇遇：{self.serendipity}"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return f"奇遇推送 {self.time}\n{self.serendipity} 被 {self.name} 抱走惹。"
