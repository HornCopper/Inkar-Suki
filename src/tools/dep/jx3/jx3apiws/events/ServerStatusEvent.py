from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=2001)
class ServerStatusEvent(RecvEvent):
    """服务器状态推送事件"""

    __event__ = "WsRecv.ServerStatus"
    message_type = "ServerStatus"
    status: bool
    """服务器状态"""

    @validator("status", pre=True)
    def check_status(cls, v):
        return v == 1

    @property
    def status_desc(self):
        status = "已开服" if self.status else "已维护"
        return status

    @property
    def log(self) -> str:
        self.record()
        log = f"开服推送事件：[{self.server}]状态-{self.status_desc}"
        return log

    def record(self):
        s: Server = self.mapped_server
        if s is None:
            return
        s_type = ServerRecordType.last_start if self.status else ServerRecordType.last_stop
        s.get_record(s_type, DateTime().timestamp())

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        time_now = DateTime().tostring('%H:%M')
        msg = f"{time_now} {self.mapped_server_name} {self.status_desc}"
        return {
            "type": "开服",
            "server": self.mapped_server,
            "msg": msg
        }
