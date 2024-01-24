from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1006)
class FireworksEvent(RecvEvent):
    """烟花播报事件"""

    __event__ = "WsRecv.Fireworks"
    message_type = "Fireworks"
    role_name: str
    """烟花地图"""
    name: str
    """接受烟花的角色"""
    sender: str
    """使用烟花的角色"""
    recipient: str
    """烟花名字"""
    time: str
    """烟花使用时间"""
    @property
    def log(self) -> str:
        log = f"烟花事件：{self.sender} 在 {self.map} 对 {self.name} 使用了烟花：{self.recipient}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return f"[烟花监控] 时间：{self.time}\n{self.sender} 在 {self.map} 对 {self.name} 使用了烟花：{self.recipient}。"
