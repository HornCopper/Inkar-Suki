"""让现有 OneBot 插件通过 QQ 官方协议处理文字与图片。"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Any

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq.event import C2CMessageCreateEvent, Event as QQEvent, GroupMessageCreateEvent
from nonebot.exception import FinishedException, IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import event_preprocessor, handle_event, run_preprocessor

from .identity import IdentityStore
from src.utils.identity import IdentityScope
from src.utils.qq_official_policy import allowed_in_unmatched_group
from .message import incoming_message, outgoing_messages

QQIncoming = C2CMessageCreateEvent | GroupMessageCreateEvent
_installed = False


class QQCompatBot(Bot):
    """每条入站消息一个回复上下文，不将虚拟 Bot 注册到全局账号列表。"""

    def __init__(self, native: QQBot, source: QQIncoming, identities: IdentityStore):
        self.native = native
        self.source = source
        self.identities = identities
        self.app_id = native.self_id
        super().__init__(native.adapter, str(identities.identify(self.app_id, "bot", self.app_id)))
        self.is_group = isinstance(source, GroupMessageCreateEvent)
        self.target = source.group_openid if self.is_group else source.get_user_id()
        scope = f"member:{self.target}" if self.is_group else "user"
        self.raw_user_id = identities.identify(self.app_id, scope, source.get_user_id())
        self.raw_group_id = identities.identify(self.app_id, "group" if self.is_group else "private", self.target)
        self.user_id = identities.resolve("user", self.raw_user_id)
        self.group_id = identities.resolve("group", self.raw_group_id) if self.is_group else self.raw_group_id
        self.sequence = 0
        self.send_lock = asyncio.Lock()
        timestamp = datetime.fromisoformat(source.timestamp.replace("Z", "+00:00"))
        self.timestamp = timestamp.replace(tzinfo = timestamp.tzinfo or timezone.utc).timestamp()

    def sender_info(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "group_id": self.group_id,
            "nickname": self.source.author.username or "QQ用户",
            "card": "",
            "role": self.source.author.member_role if self.is_group else "member",
        }

    def build_event(self) -> GroupMessageEvent:
        message = incoming_message(self.source.get_message())
        if message and message[0].is_text() and "" in self.config.command_start and "/" not in self.config.command_start:
            text = message[0].data["text"].lstrip()
            if text.startswith("/"):
                # QQ 指令常带 /，仅转换本接入消息，保留 OneBot 原有命令规则。
                message[0].data["text"] = text[1:].lstrip()
        event = GroupMessageEvent(
            time = int(self.timestamp),
            self_id = int(self.self_id),
            post_type = "message",
            message_type = "group",
            sub_type = "normal",
            message_id = self.identities.identify(self.app_id, f"message:{self.group_id}", self.source.id),
            user_id = self.user_id,
            group_id = self.group_id,
            message = message,
            original_message = message.copy(),
            raw_message = str(message),
            font = 0,
            sender = self.sender_info(),
            to_me = self.source.is_tome(),
            qq_official = True,
            private_command_proxy = True,
        )
        if not self.is_group:
            # 与 private_commands 插件相同的群上下文方式，让群限定查询也能在 C2C 中使用。
            # 发送仍按 private 路由，且每个用户拥有独立上下文。
            event.message_type = "private"  # type: ignore[assignment]
        return event

    def skip(self, reason: str) -> Any:
        logger.debug(f"QQ 官方接入跳过：{reason}")
        # Matcher 正常结束，不作为代码错误回发给用户。
        raise FinishedException

    async def call_api(self, api: str, **data: Any) -> Any:
        def same_target(scope: IdentityScope, value: Any, expected: int) -> bool:
            try:
                return self.identities.resolve(scope, value) == self.identities.resolve(scope, expected)
            except (ValueError, TypeError):
                return False

        # 区服绑定等文字功能只需当前发送者角色；直接使用官方事件中的可信字段。
        if (api == "get_group_member_info"
            and same_target("group", data.get("group_id"), self.group_id)
            and same_target("user", data.get("user_id"), self.user_id)):
            return self.sender_info()
        if api not in {"send_msg", "send_group_msg", "send_private_msg"}:
            return self.skip(f"未适配的接口 {api}")
        group_send = api == "send_group_msg" or (api == "send_msg" and data.get("message_type") == "group")
        if group_send:
            valid_target = same_target("group", data.get("group_id"), self.group_id)
        else:
            valid_target = not self.is_group and same_target("user", data.get("user_id"), self.user_id)
        if not valid_target:
            return self.skip("跨会话或主动发送")
        value = data.get("message", "")
        message = Message(value) if not data.get("auto_escape") else Message(MessageSegment.text(str(value)))
        messages = outgoing_messages(message)
        result_id = 0
        async with self.send_lock:
            for reply in messages:
                limit = 5 if self.is_group else 4
                lifetime = 300 if self.is_group else 3600
                if self.sequence >= limit or time.time() - self.timestamp >= lifetime:
                    return self.skip("被动回复次数或时间已用完")
                self.sequence += 1
                kwargs = {"message": reply, "msg_id": self.source.id, "msg_seq": self.sequence}
                logger.info(f"QQ 官方回复开始发送：msg_seq={self.sequence}，消息段={','.join(segment.type for segment in reply)}")
                if self.is_group:
                    result = await self.native.send_to_group(group_openid = self.target, **kwargs)
                else:
                    result = await self.native.send_to_c2c(openid = self.target, **kwargs)
                logger.info(f"QQ 官方回复发送成功：msg_seq={self.sequence}")
                if result.id:
                    result_id = self.identities.identify(self.app_id, "sent-message", result.id)
        return {"message_id": result_id}


def install_bridge(path: str = "src/data/qq_official.sqlite3") -> None:
    global _installed
    if _installed:
        return
    identities = IdentityStore(path)

    @run_preprocessor
    async def require_matched_group(bot: Bot, matcher: Matcher) -> None:
        if (isinstance(bot, QQCompatBot) and bot.is_group and bot.group_id < 0
            and not allowed_in_unmatched_group(matcher)):
            raise IgnoredException("QQ official group is disabled until its group number is matched")

    @event_preprocessor
    async def bridge(bot: QQBot, event: QQEvent) -> None:
        if isinstance(event, GroupMessageCreateEvent) and event.author.bot:
            raise IgnoredException("Ignore bot-authored QQ group messages")
        if isinstance(event, (C2CMessageCreateEvent, GroupMessageCreateEvent)):
            proxy = QQCompatBot(bot, event, identities)
            translated = proxy.build_event()
            if translated.message and identities.claim_message(bot.self_id, event.get_session_id(), event.id):
                await handle_event(proxy, translated)
        # 其他官方事件不进入只适用于 OneBot 的插件。
        raise IgnoredException("QQ official event handled by compatibility bridge")

    _installed = True
