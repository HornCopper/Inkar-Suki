from .WsData import *
from .RecvEvent import *


class EventRister:
    """事件注册器"""

    event_dict: dict[int, RecvEvent] = {}
    """事件映射字典"""

    @classmethod
    def rister(cls, action: int):
        def _rister(event: RecvEvent):
            cls.event_dict[action] = event
            return event

        return _rister

    @classmethod
    def get_event(cls, ws_data: WsData) -> Optional["RecvEvent"]:
        event = cls.event_dict.get(ws_data.action)
        if event:
            return event.parse_obj(ws_data.data)
        return None
