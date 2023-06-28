from ..dep import *


@EventRegister.register(action=10001)
class SubscribeEvent(RecvEvent):
    """订阅回执"""

    __event__ = "WsRecv.Subscribe"
    message_type = "Subscribe"
    user_message_type: str = '已订阅'  # 用户定义的事件名称
    action: Literal["烟花报时", "玄晶报时", "游戏消息"]
    """订阅内容"""
    server: list
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
        log = f"订阅回执，类型：{self.action}。"
        return log

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        return self.get_message()

    @overrides(RecvEvent)
    def get_message(self) -> str:
        return f"[订阅回执]\n类型：{self.action}。"
