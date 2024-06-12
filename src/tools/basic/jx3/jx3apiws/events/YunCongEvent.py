from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=2006)
class ZhuEEvent(RecvEvent):
    """
    云从推送
    """
    __event__ = "WsRecv.YunCong"
    message_type: str = "YunCong"
    name: str
    """阶段名"""
    time: int
    """获取时间"""
    desc: str
    """阶段名称"""
    site: str
    """阶段地点"""

    @property
    def log(self) -> str:
        log = f"云从预告：{self.site}的{self.name}（{self.desc}）在{self.time}开启了！"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        time_ = convert_time(int(self.time), "%H:%M")
        return {"type": "云从", "msg": f"{self.site}的{self.name}（{self.desc}）在{time_}开启了！"}
