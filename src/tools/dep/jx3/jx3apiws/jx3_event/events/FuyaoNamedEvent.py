from ..dep import *


@EventRegister.rister(action=1005)
class FuyaoNamedEvent(RecvEvent):
    """扶摇点名事件"""

    __event__ = "WsRecv.FuyaoNamed"
    message_type = "FuyaoNamed"
    user_message_type: str = '扶摇点名'  # 用户定义的事件名称
    names: list[str]
    """点名角色组"""
    time: str
    """点名时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        name = ",".join(self.names)
        log = f"扶摇点名事件：[{self.server}]的扶摇点名了，玩家[{name}] 。"
        return log

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        return self.get_message()

    @overrides(RecvEvent)
    def get_message(self) -> str:
        name = ",".join(self.names)
        return f"[扶摇监控] 时间：{self.time}\n唐文羽点名了[{name}]。"
