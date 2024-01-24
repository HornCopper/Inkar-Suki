from .api_lib.EventRister import *
from src.tools.utils import *


@EventRister.rister(action=2002)
class NewsRecvEvent(RecvEvent):
    """新闻推送事件"""

    __event__ = "WsRecv.News"
    message_type = "News"
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
    def get_message(self) -> dict:
        return {"type": "公告", "msg": f"{self.type}来啦！\n标题：{self.title}\n链接：{self.url}\n日期：{self.date}"}
