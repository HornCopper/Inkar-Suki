from .api_lib.EventRister import *
from src.tools.utils import *

@EventRister.rister(action=2005)
class NewsRecvEvent(RecvEvent):
    """烂柯山关隘首领刷新推送事件"""

    __event__ = "WsRecv.Lankeshan"
    message_type:str = "Lankeshan"
    server: str
    """服务器"""
    castle: str
    """关隘名称"""
    start: int
    """时间"""

    @property
    def log(self) -> str:
        final_time = convert_time(self.start, "%H:%M")
        log = f"关隘刷新推送：{self.server}·{self.castle}于{final_time}开启了！"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        final_time = convert_time(self.start, "%H:%M")
        return {"type": "关隘", "server": self.server, "msg": f"{self.server}·{self.castle}在 {final_time} 开启了！"}