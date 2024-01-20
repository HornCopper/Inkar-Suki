from .api_lib.EventRister import *
from src.tools.utils import *


# @EventRister.rister(action=2006)
# TODO 字段结构
class XingxiaYuncongsheEvent(RecvEvent):
    """云从社"""

    __event__ = "WsRecv.XingxiaYuncongshe"
    message_type = "XingxiaYuncongshe"
    status: bool
    """服务器状态"""

    @validator("status", pre=True)
    def check_status(cls, v):
        return v == 1

    @property
    def log(self) -> str:
        status = "已开服" if self.status else "已维护"
        log = f"云从社事件开始啦：[{self.server}]状态-{status}"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        time_now = DateTime().tostring()
        if self.status:
            return {"type": "开服", "server": self.server, "msg": f"{time_now} {self.server} 开服 (/≧▽≦)/"}
        elif not self.status:
            return {"type": "开服", "server": self.server, "msg": f"{time_now} {self.server} 维护 ヘ(~ω~ヘ) "}
