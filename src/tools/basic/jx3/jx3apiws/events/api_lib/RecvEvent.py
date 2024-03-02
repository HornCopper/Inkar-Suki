from typing import Optional, Literal
from pydantic import Extra, validator
from nonebot.adapters import Event as BaseEvent
from abc import abstractmethod
from nonebot.typing import overrides
from nonebot.utils import escape_tag
from src.tools.utils import *
from src.constant.jx3.entity.Server import Server, ServerRecordType


class RecvEvent(BaseEvent, extra=Extra.ignore):
    """ws推送事件"""

    __event__ = "WsRecv"
    post_type: str = "WsRecv"
    message_type: str
    server: Optional[str] = None
    """影响服务器"""

    @property
    def mapped_server(self) -> Server:
        return Server.from_alias(self.server)

    @property
    def mapped_server_name(self) -> str:
        s: Server = self.mapped_server
        return s.name if s else self.server

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

    @overrides(BaseEvent)
    def get_message(self) -> dict:
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
