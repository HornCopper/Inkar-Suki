"""将官方成员入群通知交给现有 OneBot 欢迎语响应器。"""

import hashlib
import json
from datetime import timezone
from typing import Any

from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, GroupIncreaseNoticeEvent, Message, MessageSegment
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq.event import GroupMemberAddEvent
from nonebot.exception import FinishedException

from src.utils.identity import IdentityStore
from .proactive import GroupPush


class QQGroupNoticeBot(Bot):
    """通知没有可借用的用户消息 ID，只允许向事件所在群主动发送文字、图片。"""

    is_group = True

    def __init__(self, native: QQBot, source: GroupMemberAddEvent, identities: IdentityStore):
        self.native = native
        self.source = source
        self.identities = identities
        self.app_id = native.self_id
        self.target = source.group_openid
        super().__init__(get_adapter(Adapter), str(identities.identify(self.app_id, "bot", self.app_id)))
        self.raw_group_id = identities.identify(self.app_id, "group", self.target)
        self.raw_user_id = identities.identify(self.app_id, f"member:{self.target}", source.member_openid)
        self.group_id = identities.resolve("group", self.raw_group_id)
        self.user_id = identities.resolve("user", self.raw_user_id)
        self.timestamp = source.timestamp.replace(tzinfo=source.timestamp.tzinfo or timezone.utc).timestamp()
        fallback = json.dumps([self.target, source.member_openid, self.timestamp], ensure_ascii=True)
        self.delivery_key = source.event_id or hashlib.sha256(fallback.encode()).hexdigest()
        self.push = GroupPush(native, self.target, self.group_id, identities, "入群欢迎")

    def log_compatibility(self, reason: str, *, action: str = "跳过欢迎语", api: str | None = None,
                          matcher: Any = None, command: str | None = None, level: str = "WARNING") -> None:
        self.push.log(reason, action=action, level=level, api=api, command=command, user_id=self.user_id,
                      event_type=type(self.source).__name__, event_id=self.source.event_id)

    def build_event(self) -> GroupIncreaseNoticeEvent:
        return GroupIncreaseNoticeEvent(
            time=int(self.timestamp), self_id=int(self.self_id), post_type="notice", notice_type="group_increase",
            sub_type="approve", group_id=self.group_id, user_id=self.user_id,
            # 官方事件未提供邀请人/审批人，0 表示未知，不把入群成员冒充操作者。
            operator_id=0, qq_official=True,
        )

    async def call_api(self, api: str, **data: Any) -> Any:
        group_send = api == "send_group_msg" or (api == "send_msg" and data.get("message_type") == "group")
        if not group_send:
            self.log_compatibility("成员入群通知仅支持向当前群发送欢迎语", api=api)
            raise FinishedException
        try:
            valid = self.identities.resolve("group", data.get("group_id")) == self.group_id and self.group_id > 0
        except (ValueError, TypeError):
            valid = False
        if not valid:
            self.log_compatibility("未匹配群号或跨群发送", api=api)
            raise FinishedException
        value = data.get("message", "")
        message = Message(MessageSegment.text(str(value))) if data.get("auto_escape") else Message(value)
        unsupported = sorted({part.type for part in message if part.type not in {"text", "image"}})
        if unsupported:
            decorative = set(unsupported).issubset({"at", "reply"})
            self.log_compatibility("暂未发送的消息段：" + ",".join(unsupported), api=api,
                                   action="省略欢迎语消息段", level="DEBUG" if decorative else "WARNING")
        message = Message(part for part in message if part.type in {"text", "image"})
        await self.push.send(message, "", delivery_key=self.delivery_key)
        return {"message_id": 0}

    def can_welcome(self) -> bool:
        if self.group_id <= 0:
            self.log_compatibility("未匹配群号，业务功能已停用")
            return False
        block = self.identities.group_delivery_block(self.app_id, self.target)
        if block:
            self.log_compatibility(block)
            return False
        from src.utils.database.operation import get_group_settings

        if "禁用欢迎语" in (get_group_settings(self.group_id, "additions") or []):
            self.log_compatibility("群设置已禁用欢迎语", level="INFO")
            return False
        return True
