from ..dep import *


@EventRegister.register(action=10002)
class DisSubscribeEvent(RecvEvent):
    """取消订阅回执"""

    __event__ = "WsRecv.DisSubscribe"
    message_type = "DisSubscribe"
    user_message_type: str = '取消订阅'  # 用户定义的事件名称
    action: Literal["烟花报时", "玄晶报时", "游戏消息"]
    """订阅内容"""
    server: list[str]
    """已订阅服务器"""

    @validator("action", pre=True)
    def check_action(cls, v):
        if v == 1006:
            return "烟花报时"
        elif v == 1007:
            return "玄晶报时"
        elif v == 1010:
            return "游戏消息"

    @property
    def log(self) -> str:
        log = f"取消订阅回执，类型：{self.action}。"
        return log

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        return self.get_message()

    @overrides(RecvEvent)
    def get_message(self) -> str:
        return f"[取消订阅回执]\n类型：{self.action}。"
