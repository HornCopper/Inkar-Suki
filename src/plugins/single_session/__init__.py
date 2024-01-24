from typing import Dict, AsyncGenerator

from nonebot.adapters import Event
from nonebot.params import Depends
from nonebot.plugin import PluginMetadata
from nonebot.message import IgnoredException, event_preprocessor

__plugin_meta__ = PluginMetadata(
    name="唯一会话",
    description="限制同一会话内同时只能运行一个响应器",
    usage="加载插件后自动生效",
    type="application",
    homepage="https://github.com/nonebot/nonebot2/blob/master/nonebot/plugins/single_session.py",
    config=None,
    supported_adapters=None,
)

_running_matcher: dict[str, int] = {}


async def matcher_mutex(event: Event):
    '''返回当前是否已在处理'''
    try:
        session_id = event.get_session_id()
    except Exception:
        yield False
        return

    current_event_id = id(event)
    if prev_event_id := _running_matcher.get(session_id):
        if prev_event_id != current_event_id:
            # 事件不一致，则说明上一个事件正在处理
            yield True
            return
        del _running_matcher[session_id]
    else:
        _running_matcher[session_id] = current_event_id
    yield False


@event_preprocessor
async def preprocess(mutex: bool = Depends(matcher_mutex)):
    if not mutex:
        return
    raise IgnoredException("Another matcher running")
