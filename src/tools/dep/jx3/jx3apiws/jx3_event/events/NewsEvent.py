from ..dep import *


@EventRegister.rister(action=2002)
class NewsRecvEvent(RecvEvent):
    """新闻推送事件"""

    __event__ = "WsRecv.News"
    message_type = "News"
    user_message_type: str = '公告'  # 用户定义的事件名称
    type: str
    """新闻类型"""
    title: str
    """新闻标题"""
    url: str
    """新闻url链接"""
    date: str
    """新闻日期"""

    @property
    def log(self) -> str:
        log = f"{self.type}事件：{self.title}"
        return log

    @overrides(RecvEvent)
    def render_message(self, group) -> str:
        return self.get_message()

    @overrides(RecvEvent)
    def get_message(self) -> str:
        return f"{self.type}来啦！\n标题：{self.title}\n链接：{self.url}\n日期：{self.date}"
