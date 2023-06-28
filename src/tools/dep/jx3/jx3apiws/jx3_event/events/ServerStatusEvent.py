from ..dep import *


@EventRegister.register(action=2001)
class ServerStatusEvent(RecvEvent):
    """服务器状态推送事件"""

    __event__ = "WsRecv.ServerStatus"
    message_type = "ServerStatus"
    user_message_type: str = '开服'  # 用户定义的事件名称
    status: bool
    """服务器状态"""

    @validator("status", pre=True)
    def check_status(cls, v):
        return v == 1

    @property
    def log(self) -> str:
        status = self.get_message()
        log = f"开服推送事件：[{self.server}]状态-{status}"
        return log

    @overrides(RecvEvent)
    def render_message(self, group):
        if not self.check_server(group):
            return None
        return f'{self.server}{self.get_message()}'

    @overrides(RecvEvent)
    def get_message(self) -> str:
        return "已开服~" if self.status else "已维护~"
