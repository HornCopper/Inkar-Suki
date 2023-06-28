from ..dep import *


@EventRegister.register(action=1004)
class FuyaoRefreshEvent(RecvEvent):

    __event__ = "WsRecv.FuyaoRefresh"
    message_type = "FuyaoRefresh"
    user_message_type: str = '扶摇'  # 用户定义的事件名称
    time: str

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        log = f"扶摇刷新事件：[{self.server}]的扶摇开始刷新 。"
        return log

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        return self.get_message()

    @overrides(RecvEvent)
    def get_message(self) -> Message:
        return f"[扶摇监控]\n扶摇九天在 {self.time} 开启了。"
