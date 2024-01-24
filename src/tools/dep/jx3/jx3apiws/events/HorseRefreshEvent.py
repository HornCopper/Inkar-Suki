from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=1002)
class HorseRefreshEvent(RecvEvent):
    """马驹刷新事件"""

    __event__ = "WsRecv.HorseRefresh"
    message_type = "HorseRefresh"
    map: str
    """刷新地图"""
    min: int
    """时间范围min"""
    max: int
    """时间范围max"""
    time: str
    """推送时间"""

    @property
    def log(self) -> str:
        log = f"马驹刷新推送：[{self.server}]的[{self.map}]将要在 {str(self.min)}-{str(self.max)} 分后刷新马驹。"
        return log

    @overrides(RecvEvent)
    def get_message(self) -> dict:
        return f"[抓马监控] 时间：{self.time}\n{self.map} 将在[{self.min} - {self.max}分]后刷新马驹。"
