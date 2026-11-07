"""官方群订阅投递，不借用用户消息或被动回复额度。"""

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq.exception import ActionFailed
from nonebot.adapters.qq.models import Media
from nonebot.log import logger

from src.utils.identity import IdentityStore
from .media import upload
from .message import outgoing_messages


@dataclass
class GroupPush:
    native: QQBot
    target: str
    group_id: int
    identities: IdentityStore
    subscribe: str
    is_group: bool = True

    def log(self, reason: str, *, action: str = "跳过推送", level: str = "WARNING", **fields: Any) -> None:
        fields = {"app_id": self.native.self_id, "group_id": self.group_id, "subscribe": self.subscribe, **fields}
        details = " ".join(f"{key}={value!r}" for key, value in fields.items() if value is not None)
        logger.bind(qq_compat=True, action=action, reason=reason, **fields).log(level,
            "QQ 官方兼容层{}：{} | {}", action, reason, details,
        )

    async def reserve(self, fingerprint: str) -> bool | None:
        reported_wait = False
        while True:
            block = self.identities.group_delivery_block(self.native.self_id, self.target)
            if block:
                self.log(block)
                return None
            day = datetime.now(timezone(timedelta(hours=8))).replace(hour=0, minute=0, second=0, microsecond=0)
            result, delay = self.identities.reserve_push(self.native.self_id, self.target, fingerprint, day.timestamp())
            if result == "ready":
                return True
            if result == "duplicate":
                return False
            if result == "daily_limit":
                self.log("已达到本群每日 1000 条主动消息的本地上限")
                return None
            if not reported_wait:
                self.log("达到主动消息分钟限额，等待额度恢复", action="延后推送")
                reported_wait = True
            await asyncio.sleep(delay)

    async def send(self, message: Message, server: str | None, *, delivery_key: str = "") -> bool:
        try:
            replies = outgoing_messages(message)
            unsupported = sorted({part.type for part in message if part.type not in {"text", "image"}})
            if unsupported:
                self.log("暂未发送的消息段：" + ",".join(unsupported), action="省略推送消息段")
            if not replies:
                self.log("推送没有可发送的文字或图片")
                return False
            digest = hashlib.sha256()
            for value in (self.subscribe, server or "", str(message)):
                encoded = value.encode("utf-8")
                digest.update(len(encoded).to_bytes(8, "big"))
                digest.update(encoded)
            if delivery_key:
                encoded = delivery_key.encode("utf-8")
                digest.update(len(encoded).to_bytes(8, "big"))
                digest.update(encoded)
            for index, reply in enumerate(replies):
                block = self.identities.group_delivery_block(self.native.self_id, self.target)
                if block:
                    self.log(block)
                    return False
                content = "".join(part.data["text"] for part in reply if part.type == "text")
                image = next((part for part in reply if part.type in {"image", "file_image"}), None)
                media = None
                if image is not None:
                    source = image.data["url"] if image.type == "image" else image.data["content"]
                    info = await upload(self, source, image.data.get("file_name") or "image.png", 1)
                    media = Media(file_info=info)
                reservation = await self.reserve(f"{digest.hexdigest()}:{index}")
                if reservation is None:
                    return False
                if not reservation:
                    continue
                # 主动发送不传 msg_id/event_id，也不占用原会话的 msg_seq。
                await self.native.post_group_messages(
                    group_openid=self.target, msg_type=7 if media else 0, content=content, media=media,
                )
                logger.info("QQ 官方订阅推送成功：app_id={!r} group_id={} subscribe={!r} part={}",
                            self.native.self_id, self.group_id, self.subscribe, index + 1)
            return True
        except ActionFailed as error:
            reason = {
                11253: "官方接口没有访问权限", 304064: "主动订阅消息未授权",
                40034100: "官方主动消息频控或配额限制", 40034101: "机器人不是该群成员",
                40034105: "主动消息发送无权限，请检查群内允许主动消息设置及应用权限",
                40054002: "机器人被禁言", 40054003: "机器人不是该群成员",
                40054010: "官方拒绝消息中的 URL，需检查应用链接权限",
            }.get(error.code, "官方主动消息接口拒绝发送")
            self.log(reason, action="推送失败", code=error.code, status=error.status_code)
        except Exception as error:
            # 异常文本可能包含正文、图片路径或响应体，只记录异常类型。
            self.log("主动推送发生异常", action="推送失败", error_type=type(error).__name__)
        return False


async def send_group_subscription(
    native: QQBot, identities: IdentityStore, group_id: int, subscribe: str, message: str | Message, server: str | None,
) -> bool:
    group_id = identities.resolve("group", group_id)
    target = identities.lookup(native.self_id, "group", group_id)
    if target is None:
        return False
    push = GroupPush(native, target, group_id, identities, subscribe)
    if group_id <= 0:
        push.log("未匹配群号，业务推送已停用")
        return False
    block = identities.group_delivery_block(native.self_id, target)
    if block:
        push.log(block)
        return False
    return await push.send(Message(message), server)
