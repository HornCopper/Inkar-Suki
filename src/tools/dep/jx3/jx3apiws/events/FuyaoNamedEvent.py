from .api_lib.EventRister import *
from src.tools.utils import *



@EventRister.rister(action=1005)
class FuyaoNamedEvent(RecvEvent):
    """扶摇点名事件"""

    __event__ = "WsRecv.FuyaoNamed"
    message_type = "FuyaoNamed"
    name: list[str]
    """点名角色组"""
    time: int
    """点名时间"""
    server: str
    """服务器"""


    @property
    def log(self) -> str:
        name = "、".join(self.name)
        log = f"扶摇点名事件：[{self.server}]的扶摇点名了，玩家[{name}] 。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        name = "、".join(self.name)
        final_time = convert_time(self.time, format="%H:%M")
        return {"type": "扶摇", "msg": f"{self.server}的唐文羽在{final_time}点名了[{name}]，请速速前往少林！", "server": f"{self.server}"}
