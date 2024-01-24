from .api_lib.EventRister import *
from src.tools.utils import *



@EventRister.rister(action=1005)
class FuyaoNamedEvent(RecvEvent):
    """扶摇点名事件"""

    __event__ = "WsRecv.FuyaoNamed"
    message_type = "FuyaoNamed"
    names: list[str]
    """点名角色组"""
    time: str
    """点名时间"""


    @property
    def log(self) -> str:
        name = ",".join(self.names)
        log = f"扶摇点名事件：[{self.server}]的扶摇点名了，玩家[{name}] 。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        name = ",".join(self.names)
        return f"[扶摇监控] 时间：{self.time}\n唐文羽点名了[{name}]。"
