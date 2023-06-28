from ..dep import *


@EventRegister.register(action=1006)
class FireworksEvent(RecvEvent):
    """烟花播报事件"""

    __event__ = "WsRecv.Fireworks"
    message_type = "Fireworks"
    user_message_type: str = '烟花'  # 用户定义的事件名称
    role: str
    """烟花地图"""
    name: str
    """接受烟花的角色"""
    sender: str
    """使用烟花的角色"""
    recipient: str
    """烟花名字"""
    time: str
    """烟花使用时间"""

    @validator("time", pre=True)
    def check_time(cls, v):
        start_trans = datetime.fromtimestamp(int(v))
        return start_trans.strftime("%H:%M:%S")

    @property
    def log(self) -> str:
        log = f"烟花事件：{self.sender} 在 {self.map} 对 {self.name} 使用了烟花：{self.recipient}。"
        return log

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        return self.get_message()

    @overrides(RecvEvent)
    def get_message(self) -> str:
        return f"[烟花监控] 时间：{self.time}\n{self.sender} 在 {self.map} 对 {self.name} 使用了烟花：{self.recipient}。"
