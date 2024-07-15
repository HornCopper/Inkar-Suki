from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1001)
class SerendipityEvent(RecvEvent):
    """奇遇播报事件"""

    __event__ = "WsRecv.Serendipity"
    message_type: str = "Serendipity"
    zone: str
    """游戏大区"""
    server: str
    """服务器"""
    name: str
    """角色名称"""
    event: str
    """奇遇名称"""
    level: int
    """绝世"""
    time: int
    """时间戳"""

    @property
    def log(self) -> str:
        log = f"奇遇推送事件：[{self.server}]的[{self.name}]抱走了奇遇：{self.event}"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        if self.event in ["泛天河", "庆舞良宵", "拜春擂"]:
            return {"type": ""}
        final_time = convert_time(self.time, "%H:%M")
        msg = f"{self.server} 的[{self.name}]在 {final_time} 抱走了奇遇「{self.event}」!"
        return {"type": "奇遇", "server": self.server, "msg": msg, "level": self.level}