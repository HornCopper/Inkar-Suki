from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1004)
class FuyaoRefreshEvent(RecvEvent):

    __event__ = "WsRecv.FuyaoRefresh"
    message_type = "FuyaoRefresh"
    server: str
    """服务器"""
    time: int
    """时间"""



    @property
    def log(self) -> str:
        log = f"扶摇刷新事件：[{self.server}]的扶摇已刷新 。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        final_time = convert_time(self.time, format="%H:%M")
        return {"type": "扶摇", "server": self.server, "msg": f"{self.server}的扶摇九天在{final_time}开启啦，请前往少林演武场参加试炼！"}
