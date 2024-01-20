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
    def log(self) -> str:
        status = "已开服" if self.status else "已维护"
        log = f"开服推送事件：[{self.server}]状态-{status}"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        time_now = DateTime('%H:%M')
        if self.status:
            return {"type": "开服", "server": self.server, "msg": f"{time_now} {self.server} 开服 (/≧▽≦)/"}
        elif not self.status:
            return {"type": "开服", "server": self.server, "msg": f"{time_now} {self.server} 维护 ヘ(~ω~ヘ) "}

