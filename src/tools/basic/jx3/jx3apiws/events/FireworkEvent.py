from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1006)
class FireworkEvent(RecvEvent):
    """烟花事件"""

    __event__ = "WsRecv.Firework"
    message_type = "Firework"
    time: int
    """点名时间"""
    server: str
    """服务器"""
    map_name: str
    """接收地图"""
    sender: str
    """发送方"""
    recipient: str
    """接收方"""
    name: str
    """烟花名称"""

    @property
    def log(self) -> str:
        log = f"{self.server} 的 {self.sender} 在 {self.map_name} 给 {self.recipient} 赠送了烟花「{self.name}」！"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        final_time = convert_time(self.time, format="%H:%M")
        return {"type": "烟花", "msg": f"{self.server} 的 {self.sender} 于 {final_time} 在 {self.map_name} 给 {self.recipient} 赠送了烟花「{self.name}」！", "server": f"{self.server}"}
