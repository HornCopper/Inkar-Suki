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
    time: str
    """获取时间"""
    server: str

    @property
    def log(self) -> str:
        log = f"玄晶事件：【{self.server}】[{self.time}] 侠士 {self.role_name} 在 {self.map_name} 获取了 {self.name}。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return {"type": "玄晶", "server": f"{self.server}", "msg": f"{self.time}\n【{self.server}】恭喜侠士[{self.role_name}]在{self.map_name}获得稀有掉落[{self.name}]！"}
