from src.tools.dep import *
from typing import Dict, Optional, Dict, Any

from nonebot.adapters import Bot, Event
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

_running_matcher: dict[str, tuple[int, int]] = {}  # {session:[event,time]}
_blocking_bot: dict[str, dict[str, str]] = filebase_database.Database(
    f'{bot_path.common_data_full}blocking-bot',
).value


def get_blocking_status(bot_qq: str):
    bot_qq = str(bot_qq)
    data = _blocking_bot.get(bot_qq)
    if data is None:
        data = {
            'slient_to': 0,
            'failed_time': 0,
        }
        _blocking_bot[bot_qq] = data

    return data


@Bot.on_called_api
async def handle_api_result(
    bot: Bot, exception: Optional[Exception], api: str, data: Dict[str, Any], result: Any
):
    if api != "send_msg":
        return
    msg = str(data.get('message') or '')[0:50]

    x_data = {
        'user_id': data.get('user_id'),
        'group_id': data.get('group_id'),
        'message_type': data.get('message_type'),
        'message': msg,
    }
    logger.debug(f'[on_called_api.{api}]exception={exception},data:{x_data}')
    bot_qq = str(bot.self_id)
    data = get_blocking_status(bot_qq)

    if exception is None:
        # 未被风控，则减少
        data['failed_time'] = 0
        data['slient_to'] -= - 1
        if data['slient_to'] < 0:
            data['slient_to'] = 0
        return

    # 60*(1+n^2)秒内不再处理消息
    data['failed_time'] += 1
    block_time = 60 * (1 + pow(data['failed_time'], 2))
    data['slient_to'] = int(DateTime().timestamp() + block_time)
    logger.warning(f'{bot_qq}账号连续消息发送失败{data["failed_time"]}次。下次尝试:{DateTime(data["slient_to"])}')


async def matcher_mutex(bot: Bot, event: Event):
    '''返回当前是否已在处理'''
    try:
        session_id = event.get_session_id()
    except Exception:
        return False

    slient_status = get_blocking_status(bot.self_id)
    prev_event = _running_matcher.get(session_id)
    if slient_status.get('slient_to') > DateTime().timestamp():
        if prev_event:
            del _running_matcher[session_id]
        return True

    current_event_id = id(event)
    if prev_event:
        prev_event_id, prev_time = prev_event
        if prev_event_id != current_event_id and prev_time > DateTime().timestamp():
            # 事件不一致，则说明上一个事件正在处理
            return True
        del _running_matcher[session_id]
        return False

    _running_matcher[session_id] = [
        current_event_id,
        int(DateTime().timestamp() + 7),  # 7秒未响应则取消锁定
    ]
    return False

__session_lock = threading.Lock()


@event_preprocessor
async def preprocess(mutex: bool = Depends(matcher_mutex)):
    with __session_lock:
        if not mutex:
            return
        raise IgnoredException("Another matcher running")
