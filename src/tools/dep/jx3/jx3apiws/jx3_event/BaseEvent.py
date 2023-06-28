from src.tools.dep.data_server import *
from src.tools.file import *
from abc import abstractmethod
from datetime import datetime
from typing import Literal, Optional

from nonebot.adapters import Event as BaseEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.typing import overrides
from nonebot.utils import escape_tag
from pydantic import BaseModel, Extra, validator

import json

import nonebot
import sys

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(str(TOOLS))
ASSETS = TOOLS[:-5] + "assets"

'''
感谢友情提供代码@白师傅
原链接：
https://github.com/JustUndertaker/mini_jx3_bot
'''


class EventRegister:
    """事件注册器"""

    event_dict: dict[int, "RecvEvent"] = {}
    """事件映射字典"""

    @classmethod
    def register(cls, action: int):
        def _register(event: "RecvEvent"):
            cls.event_dict[action] = event
            return event

        return _register

    @classmethod
    def get_event(cls, ws_data: "WsData") -> Optional["RecvEvent"]:
        event = cls.event_dict.get(ws_data.action)
        if not event:
            return None
        return event.parse_obj(ws_data.data)


class WsData(BaseModel):
    """
    ws数据模型
    """

    action: int
    """ws消息类型"""
    data: dict
    """消息数据"""


class WsNotice(BaseEvent):
    """ws通知主人事件"""

    __event__ = "WsNotice"
    post_type: str = "WsNotice"
    message: str
    """通知内容"""

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return self.post_type

    @overrides(BaseEvent)
    def get_event_name(self) -> str:
        return self.post_type

    @overrides(BaseEvent)
    def get_event_description(self) -> str:
        return escape_tag(str(self.dict()))

    @overrides(BaseEvent)
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_plaintext(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_user_id(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_session_id(self) -> str:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def is_tome(self) -> bool:
        return False


class RecvEvent(BaseEvent, extra=Extra.ignore):
    """ws推送事件"""

    __event__ = "WsRecv"
    post_type: str = "WsRecv"
    message_type: str
    user_message_type:str = '未知事件' # 用户定义的事件名称 
    server: Optional[str] = None
    """影响服务器"""

    @property
    @abstractmethod
    def log(self) -> str:
        """事件日志内容"""
        raise NotImplementedError

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return self.post_type

    @overrides(BaseEvent)
    def get_event_name(self) -> str:
        message_type = getattr(self, "message_type", None)
        return f"{self.post_type}" + (f".{message_type}" if message_type else "")

    @overrides(BaseEvent)
    def get_event_description(self) -> str:
        return escape_tag(str(self.dict()))

    @abstractmethod
    def get_message(self) -> str:
        return '[get message]'

    @abstractmethod
    def render_message(self, group) -> str:
        return '[render message]'

    def check_server(self, group) -> bool:
        return server_mapping(group_id=group) == server_mapping(self.server)

    @overrides(BaseEvent)
    def get_plaintext(self) -> str:
        return '[get_plaintext]'

    @overrides(BaseEvent)
    def get_user_id(self) -> str:
        return '[get_user_id]'

    @overrides(BaseEvent)
    def get_session_id(self) -> str:
        return '[get_session_id]'

    @overrides(BaseEvent)
    def is_tome(self) -> bool:
        return False

