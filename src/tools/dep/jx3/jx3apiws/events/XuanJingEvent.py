from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1007)
class XuanJingEvent(RecvEvent):
    """玄晶获取事件"""

    __event__ = "WsRecv.XuanJing"
    message_type = "XuanJing"
    role_name: str
    """角色名"""
    map_name: str
    """地图名"""
    name: str
    """玄晶名"""
    time: int
    """获取时间"""
    server: str
    """服务器"""

    @property
    def log(self) -> str:
        final_time = convert_time(self.time, "%H:%M")
        log = f"玄晶事件：【{self.server}】[{final_time}] 侠士 {self.role_name} 在 {self.map_name} 获取了 {self.name}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        final_time = convert_time(self.time, "%H:%M")
        return {"type": "玄晶", "server": f"{self.server}", "msg": f"{self.server}的{self.name}在{final_time}被{self.role_name}从{self.map_name}中拍走啦！"}
