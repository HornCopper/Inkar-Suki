from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1004)
class FuyaoRefreshEvent(RecvEvent):

    __event__ = "WsRecv.FuyaoRefresh"
    message_type = "FuyaoRefresh"
    time: str



    @property
    def log(self) -> str:
        log = f"扶摇刷新事件：[{self.server}]的扶摇开始刷新 。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return f"[扶摇监控]\n扶摇九天在 {self.time} 开启了。"
