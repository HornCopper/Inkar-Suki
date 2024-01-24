from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1009)
class ZhuEEvent(RecvEvent):
    """
    诛恶事件推送
    """
    __event__ = "WsRecv.ZhuE"
    message_type = "ZhuE"
    map_name: str
    """地图名"""
    time: str
    """获取时间"""
    server: str

    @property
    def log(self) -> str:
        log = f"诛恶事件：{self.time} {self.server} 的 诛恶事件 在 {self.map_name}触发了！"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return {"type": "诛恶", "server": self.server, "msg": f"现在是{self.time}了！{Config.name}提醒各位：\n{self.server} 的 诛恶事件 在 {self.map_name} 触发啦，快前往该地图吧！"}
