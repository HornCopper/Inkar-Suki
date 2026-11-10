"""让现有 OneBot 插件通过 QQ 官方协议处理文字与图片。"""

import asyncio
import time
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from nonebot import get_adapter, get_driver
from nonebot.adapters.onebot.v11 import Adapter as OneBotAdapter, Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq.event import (
    C2CMessageCreateEvent, Event as QQEvent, GroupMessageCreateEvent,
    GroupAddRobotEvent, GroupDelRobotEvent, GroupMsgReceiveEvent, GroupMsgRejectEvent, GroupMemberAddEvent,
)
from nonebot.adapters.qq.exception import ActionFailed
from nonebot.exception import FinishedException, IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher, current_matcher
from nonebot.message import event_preprocessor, handle_event, run_preprocessor
from nonebot.typing import T_State

from .identity import IdentityStore
from src.utils.qq_official_policy import allowed_in_unmatched_group
from .api import ContextAPI, UNHANDLED, UNSUPPORTED_APIS, unavailable
from .dispatch import install_command_prefilter
from .media import DIRECT_UPLOAD_LIMIT, file_source, send_media
from .message import incoming_message, outgoing_messages
from .notice import QQGroupNoticeBot

QQIncoming = C2CMessageCreateEvent | GroupMessageCreateEvent
_installed = False
_active_api: ContextVar[str | None] = ContextVar("qq_official_active_api", default = None)


class QQCompatBot(Bot):
    """每条入站消息一个回复上下文，不将虚拟 Bot 注册到全局账号列表。"""

    def __init__(self, native: QQBot, source: QQIncoming, identities: IdentityStore):
        self.native = native
        self.source = source
        self.identities = identities
        self.app_id = native.self_id
        # 下游收到的是 OneBot 事件与消息段，Alconna/UniSeg 等也必须按 OneBot 解析。
        # 官方连接仅保留在 native，所有实际发送仍经本兼容层转换回 QQ 协议。
        super().__init__(get_adapter(OneBotAdapter), str(identities.identify(self.app_id, "bot", self.app_id)))
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
        self.api = ContextAPI(self)
        self._compat_logs: set[tuple[str, str | None, str]] = set()

    def sender_info(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "group_id": self.group_id,
            "nickname": self.source.author.username or "QQ用户",
            "card": "",
            "role": self.source.author.member_role if self.is_group else "member",
        }

    def build_event(self) -> GroupMessageEvent:
        original = self.source.get_message()
        unsupported = sorted({segment.type for segment in original if segment.type not in {"text", "image"}})
        if unsupported:
            self.log_compatibility("收到暂未适配的消息段：" + ",".join(unsupported), action = "省略入站消息段")
        if any(segment.type == "image" and not str(segment.data["url"]).startswith(("http://", "https://", "//")) for segment in original):
            self.log_compatibility("图片附件地址不是 HTTP/HTTPS 地址", action = "省略入站图片")
        message = incoming_message(original)
        if not message and not unsupported:
            self.log_compatibility("消息没有可处理的文字或图片", action = "跳过消息")
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

    def log_compatibility(
        self, reason: str, *, action: str = "跳过", api: str | None = None,
        official_api: str | None = None, matcher: Matcher | None = None, command: str | None = None,
        code: int | None = None, status: int | None = None, level: str = "WARNING",
    ) -> None:
        api = api or _active_api.get()
        key = (action, api, reason)
        if key in self._compat_logs:
            return
        self._compat_logs.add(key)
        matcher = matcher or current_matcher.get(None)
        if matcher is not None:
            command = command or matcher.state.get("_prefix", {}).get("raw_command")
        fields = {
            "app_id": self.app_id, "group_id": self.group_id, "user_id": self.user_id,
            "message_id": self.source.id, "api": api, "official_api": official_api,
            "command": command,
            "matcher": str(type(matcher)) if matcher is not None else None,
            "code": code, "status": status,
        }
        # 只记录诊断所需标识；不输出正文、API 参数、附件地址或服务端响应体。
        details = " ".join(f"{name}={value!r}" for name, value in fields.items() if value is not None)
        logger.bind(qq_compat=True, action=action, reason=reason, **fields).log(level, f"QQ 官方兼容层{action}：{reason} | {details}")

    def skip(self, reason: str, **diagnostic: Any) -> Any:
        self.log_compatibility(reason, **diagnostic)
        # Matcher 正常结束，不作为代码错误回发给用户。
        raise FinishedException

    def ensure_reply_available(self, check_count: bool = True) -> None:
        limit = 5 if self.is_group else 4
        lifetime = 300 if self.is_group else 3600
        if (check_count and self.sequence >= limit) or time.time() - self.timestamp >= lifetime:
            self.skip("被动回复次数或时间已用完")

    def reply_id(self, result: Any) -> int:
        return self.identities.identify(self.app_id, "sent-message", result.id) if result.id else 0

    async def call_api(self, api: str, **data: Any) -> Any:
        token = _active_api.set(api)
        try:
            return await self._dispatch_api(api, **data)
        except ActionFailed as error:
            if unavailable(error):
                self.log_compatibility("官方接口不可用或无访问权限", code = error.code, status = error.status_code)
            raise
        finally:
            _active_api.reset(token)

    async def _dispatch_api(self, api: str, **data: Any) -> Any:
        result = await self.api.call(api, data)
        if result is not UNHANDLED:
            return result
        same_target = self.api.same_target
        if api in {"upload_group_file", "upload_private_file"}:
            if api == "upload_group_file":
                valid = self.is_group and same_target("group", data.get("group_id"), self.group_id)
            else:
                valid = not self.is_group and same_target("user", data.get("user_id"), self.user_id)
            if not valid:
                return self.skip("跨会话文件上传")
            if data.get("folder"):
                return self.skip("官方文件接口不支持 OneBot 群文件夹")
            async with self.send_lock:
                self.ensure_reply_available()
                source = file_source(data.get("file", ""))
                self.sequence += 1
                result = await send_media(self, source, data.get("name", "file.bin"), 4, "", self.sequence)
            return {"message_id": self.reply_id(result)}
        if api not in {"send_msg", "send_group_msg", "send_private_msg"}:
            return self.skip("接口尚未适配")
        group_send = api == "send_group_msg" or (api == "send_msg" and data.get("message_type") == "group")
        if group_send:
            valid_target = same_target("group", data.get("group_id"), self.group_id)
        else:
            valid_target = not self.is_group and same_target("user", data.get("user_id"), self.user_id)
        if not valid_target:
            return self.skip("跨会话或主动发送")
        value = data.get("message", "")
        message = Message(value) if not data.get("auto_escape") else Message(MessageSegment.text(str(value)))
        if self.api.notes:
            message += MessageSegment.text("\n注：" + "".join(sorted(self.api.notes)))
        messages = outgoing_messages(message)
        unsupported = sorted({segment.type for segment in message if segment.type not in {"text", "image"}})
        if unsupported:
            decorative = set(unsupported).issubset({"at", "reply"})
            self.log_compatibility(
                "暂未发送的消息段：" + ",".join(unsupported), action = "省略出站消息段" if messages else "跳过回复",
                level = "DEBUG" if decorative and messages else "WARNING",
            )
        elif not messages:
            self.log_compatibility("回复没有可发送的文字或图片", action = "跳过回复")
        result_id = 0
        async with self.send_lock:
            for reply in messages:
                self.ensure_reply_available()
                self.sequence += 1
                kwargs = {"message": reply, "msg_id": self.source.id, "msg_seq": self.sequence}
                logger.info(f"QQ 官方回复开始发送：msg_seq={self.sequence}，消息段={','.join(segment.type for segment in reply)}")
                binary = next((segment for segment in reply if segment.type == "file_image"), None)
                content = binary.data["content"] if binary is not None else None
                if isinstance(content, bytes) and len(content) > DIRECT_UPLOAD_LIMIT:
                    text = "".join(segment.data["text"] for segment in reply if segment.type == "text")
                    result = await send_media(self, content, binary.data.get("file_name") or "image.png", 1, text, self.sequence)
                elif self.is_group:
                    result = await self.native.send_to_group(group_openid = self.target, **kwargs)
                else:
                    result = await self.native.send_to_c2c(openid = self.target, **kwargs)
                logger.info(f"QQ 官方回复发送成功：msg_seq={self.sequence}")
                result_id = self.reply_id(result) or result_id
        return {"message_id": result_id}


def install_bridge(path: str = "src/data/qq_official.sqlite3") -> None:
    global _installed
    if _installed:
        return
    identities = IdentityStore(path)
    install_command_prefilter(QQCompatBot)

    @get_driver().on_bot_connect
    async def report_welcome_subscription(bot: QQBot) -> None:
        if isinstance(bot, QQBot) and bot.bot_info.use_websocket and not bot.bot_info.intent.group_members:
            logger.bind(qq_compat=True, action="欢迎语配置提示", app_id=bot.self_id).warning(
                "QQ 官方欢迎语尚未启用：未订阅群成员事件；获平台授权后配置 qq_official.group_member_events=true | app_id={!r}",
                bot.self_id,
            )

    @run_preprocessor
    async def require_matched_group(bot: Bot, matcher: Matcher, state: T_State) -> None:
        if (isinstance(bot, (QQCompatBot, QQGroupNoticeBot)) and bot.is_group and bot.group_id < 0
            and not allowed_in_unmatched_group(matcher)):
            bot.log_compatibility("未匹配群号，业务功能已停用", action = "跳过功能", matcher = matcher,
                                  command = state.get("_prefix", {}).get("raw_command"))
            raise IgnoredException("QQ official group is disabled until its group number is matched")
        if isinstance(bot, QQCompatBot):
            # 连同确认步骤一起跳过确实没有官方对应接口的功能，避免先提示成功再中断。
            for handler in matcher.handlers:
                code = getattr(handler.call, "__code__", None)
                names = (*code.co_names, *(value for value in code.co_consts if isinstance(value, str))) if code else ()
                blocked = UNSUPPORTED_APIS.intersection(names)
                if blocked:
                    bot.log_compatibility("功能依赖尚未适配的接口", action = "跳过功能", api = ",".join(sorted(blocked)),
                                          matcher = matcher, command = state.get("_prefix", {}).get("raw_command"))
                    raise IgnoredException("Matcher requires an API unavailable on QQ official bots")

    @event_preprocessor
    async def bridge(bot: QQBot, event: QQEvent) -> None:
        if isinstance(event, GroupMessageCreateEvent) and event.author.bot:
            raise IgnoredException("Ignore bot-authored QQ group messages")
        if isinstance(event, (C2CMessageCreateEvent, GroupMessageCreateEvent)):
            proxy = QQCompatBot(bot, event, identities)
            if identities.claim_message(bot.self_id, event.get_session_id(), event.id):
                if proxy.is_group:
                    identities.observe_group(bot.self_id, proxy.target, joined=True, timestamp=proxy.timestamp)
                translated = proxy.build_event()
                if translated.message:
                    await handle_event(proxy, translated)
        elif isinstance(event, GroupMemberAddEvent):
            proxy = QQGroupNoticeBot(bot, event, identities)
            if identities.claim_message(bot.self_id, "member-add:" + event.group_openid, proxy.delivery_key):
                identities.observe_group(bot.self_id, proxy.target, joined=True, timestamp=proxy.timestamp)
                if proxy.can_welcome():
                    await handle_event(proxy, proxy.build_event())
        elif isinstance(event, (GroupAddRobotEvent, GroupDelRobotEvent, GroupMsgReceiveEvent, GroupMsgRejectEvent)):
            raw_group = identities.identify(bot.self_id, "group", event.group_openid)
            timestamp = event.timestamp.replace(tzinfo=event.timestamp.tzinfo or timezone.utc).timestamp()
            joined = not isinstance(event, GroupDelRobotEvent) if isinstance(event, (GroupAddRobotEvent, GroupDelRobotEvent)) else None
            allowed = isinstance(event, GroupMsgReceiveEvent) if isinstance(event, (GroupMsgReceiveEvent, GroupMsgRejectEvent)) else None
            identities.observe_group(bot.self_id, event.group_openid, joined=joined, allowed=allowed, timestamp=timestamp)
            logger.info("QQ 官方群推送状态已更新：app_id={!r} group_id={} event_type={!r}",
                        bot.self_id, identities.resolve("group", raw_group), type(event).__name__)
        else:
            event_name = type(event).__name__
            logger.bind(qq_compat=True, action="跳过事件", app_id=bot.self_id, event_type=event_name).warning(
                "QQ 官方兼容层跳过事件：事件尚未适配 | app_id={!r} event_type={!r}", bot.self_id, event_name,
            )
        # 其他官方事件不进入只适用于 OneBot 的插件。
        raise IgnoredException("QQ official event handled by compatibility bridge")

    _installed = True
