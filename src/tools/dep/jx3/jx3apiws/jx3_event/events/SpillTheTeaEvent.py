from ..dep import *


@EventRister.rister(action=2004)
class SpillTheTeaEvent(RecvEvent):
    """818推送事件"""

    __event__ = "WsRecv.SpillTheTea"
    message_type = "SpillTheTea"
    user_message_type: str = '818'  # 用户定义的事件名称
    server: str
    """服务器名"""
    name: str
    """吧名"""
    title: str
    """标题"""
    url: str
    """链接"""

    @property
    def log(self) -> str:
        log = f"吃瓜推送事件：[{self.title}]"
        return log

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        server = getGroupServer(group)
        if not server == self.server:
            return None
        return self.get_message().get('msg')

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        return self.get_message()

    @overrides(RecvEvent)
    def get_message(self) -> str:
        return f"有新的八卦推送来啦！\n{self.title}\n{self.url}\n来源：{self.name}吧"
