from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=2004)
class SpillTheTeaEvent(RecvEvent):
    """818推送事件"""

    __event__ = "WsRecv.SpillTheTea"
    message_type = "SpillTheTea"
    server: str
    """服务器名"""
    name: str
    """吧名"""
    title: str
    """标题"""
    url: str
    """链接"""

    @property
    def log(self) -> str:
        log = f"吃瓜推送事件：[{self.title}]"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return {"type": "818", "name": self.name, "msg": f"有新的八卦推送来啦！\n{self.title}\n{self.url}\n来源：{self.name}吧"}
