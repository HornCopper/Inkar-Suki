from contextvars import ContextVar
from typing import Any

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor, handle_event

from src.config import Config


_PRIVATE_REPLY_USER: ContextVar[int | None] = ContextVar("private_reply_user", default=None)
_PRIVATE_REPLY_GROUP: ContextVar[int | None] = ContextVar("private_reply_group", default=None)

_ORIGINAL_CALL_API = Bot.call_api


async def _private_command_call_api(bot: Bot, api: str, **data: Any) -> Any:
    user_id = _PRIVATE_REPLY_USER.get()
    group_id = _PRIVATE_REPLY_GROUP.get()

    if user_id is not None and group_id is not None:
        if api == "send_msg" and data.get("message_type") == "private":
            data.pop("group_id", None)
        elif api == "send_group_msg" and str(data.get("group_id")) == str(group_id):
            data.pop("group_id", None)
            data["user_id"] = user_id
            return await _ORIGINAL_CALL_API(bot, "send_private_msg", **data)

    return await _ORIGINAL_CALL_API(bot, api, **data)


if not getattr(Bot.call_api, "private_command_patch", False):
    _private_command_call_api.private_command_patch = True  # type: ignore[attr-defined]
    Bot.call_api = _private_command_call_api  # type: ignore[method-assign]


def _build_private_group_event(event: MessageEvent, group_id: int) -> GroupMessageEvent:
    data = event.model_dump()
    data["message_type"] = "group"
    data["group_id"] = group_id
    data["anonymous"] = None

    proxy_event = GroupMessageEvent(**data)
    proxy_event.message_type = "private"
    proxy_event.private_command_proxy = True
    return proxy_event


@event_preprocessor
async def _(bot: Bot, event: MessageEvent):
    if getattr(event, "private_command_proxy", False):
        return
    if event.message_type != "private":
        return
    if not Config.bot_basic.allow_private_commands:
        return

    group_id = Config.bot_basic.private_command_group_id
    if group_id <= 0:
        return

    proxy_event = _build_private_group_event(event, group_id)
    user_token = _PRIVATE_REPLY_USER.set(event.user_id)
    group_token = _PRIVATE_REPLY_GROUP.set(group_id)
    try:
        await handle_event(bot, proxy_event)
    finally:
        _PRIVATE_REPLY_USER.reset(user_token)
        _PRIVATE_REPLY_GROUP.reset(group_token)

    raise IgnoredException("Private command handled as group command.")
