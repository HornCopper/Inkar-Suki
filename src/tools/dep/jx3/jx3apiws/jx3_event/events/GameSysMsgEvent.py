from ..dep import *


@EventRister.rister(action=1008)
class GameSysMsgEvent(RecvEvent):
    """游戏系统频道消息推送"""

    __event__ = "WsRecv.GameSysMsg"
    message_type = "GameSysMsg"
    user_message_type: str = '系统'  # 用户定义的事件名称
    message: str
    """消息内容"""
    time: str
    """消息时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        log = f"系统频道推送：{self.message}。"
        return log

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        return self.get_message()

    @overrides(RecvEvent)
    def get_message(self) -> str:
        return f"[系统频道推送]\n时间：{self.time}\n{self.message}。"
