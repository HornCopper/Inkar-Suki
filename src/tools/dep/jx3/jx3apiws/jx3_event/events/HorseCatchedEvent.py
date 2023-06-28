from ..dep import *


@EventRister.rister(action=1003)
class HorseCatchedEvent(RecvEvent):
    """马驹捕获事件"""

    __event__ = "WsRecv.HorseCatched"
    message_type = "HorseCatched"
    user_message_type: str = '抓马'  # 用户定义的事件名称
    name: str
    """触发角色名"""
    map: str
    """地图"""
    horse: str
    """马驹名"""
    time: str
    """事件时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        log = f"马驹被抓事件：[{self.server}]的[{self.name}]在[{self.map}]捕获了 {self.horse} 。"
        return log

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        return self.get_message()

    @overrides(RecvEvent)
    def get_message(self) -> str:
        return f"[抓马监控] 时间：{self.time}\n{self.map} 的 {self.horse} 被 {self.name} 抓走了~"
