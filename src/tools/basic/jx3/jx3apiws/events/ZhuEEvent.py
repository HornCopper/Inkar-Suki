from .api_lib.EventRister import *
from src.tools.basic import *


@EventRister.rister(action=1009)
class ZhuEEvent(RecvEvent):
    """
    诛恶事件推送
    """
    __event__ = "WsRecv.ZhuE"
    message_type = "ZhuE"
    map_name: str
    """地图名"""
    time: int
    """获取时间"""
    server: str

    @property
    def log(self) -> str:
        final_time = convert_time(self.time, "%H:%M")
        log = f"诛恶事件：{final_time} {self.server} 的 诛恶事件 在 {self.map_name}触发了！"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        final_time = convert_time(self.time, "%H:%M")
        return {"type": "诛恶", "server": self.server, "msg": f"{self.server} 的诛恶事件于 {final_time} 在 {self.map_name} 触发啦，快前往该地图吧！"}
