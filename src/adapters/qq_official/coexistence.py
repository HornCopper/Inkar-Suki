"""仅对已匹配群号的纯文字消息执行 OneBot 优先仲裁。"""

import asyncio

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.message import event_preprocessor

from src.utils.group_message_claims import GroupMessageClaims
from src.utils.identity import IdentityStore
from src.utils.qq_official_config import QQCoexistenceConfig


def message_text(bot: Bot, event: GroupMessageEvent) -> str | None:
    text = []
    for segment in event.message:
        if segment.type == "text":
            text.append(segment.data["text"])
        elif segment.type == "reply" or (segment.type == "at" and str(segment.data.get("qq")) == bot.self_id):
            continue
        else:
            # 图片、附件及提及其他成员不按纯文本合并，避免丢失业务参数。
            return None
    content = "".join(text).strip()
    if "/" in bot.config.command_start and content.startswith("/"):
        content = content[1:].lstrip()
    if not content:
        return None
    # 官方身份查询不能被没有该接口的 OneBot 提前认领，保留配置的命令前缀。
    for prefix in bot.config.command_start | {""}:
        if content.startswith(prefix):
            command = content[len(prefix):].split(maxsplit = 1)
            if command and command[0] in {"官号信息", "qq身份"}:
                return None
    return content


def install_coexistence(identities: IdentityStore, config: QQCoexistenceConfig) -> None:
    from . import QQCompatBot

    claims = GroupMessageClaims(identities, config)

    @event_preprocessor
    async def prefer_onebot(bot: Bot, event: GroupMessageEvent) -> None:
        if not config.enabled or event.message_type != "group" or event.group_id <= 0:
            return
        content = message_text(bot, event)
        if content is None:
            return
        official = isinstance(bot, QQCompatBot)
        if official and any(segment.type != "text" for segment in bot.source.get_message()):
            # 兼容层可能已省略原消息中的非文字段，不能将剩余正文当成完整消息。
            return
        if not official and not await asyncio.to_thread(claims.has_official_group, event.group_id):
            return
        accepted = await claims.accept(event.group_id, content, official = official)
        logger.debug("群消息共存仲裁：group_id={} protocol={} accepted={}",
                     event.group_id, "official" if official else "onebot", accepted)
        if not accepted:
            raise IgnoredException("Group message already claimed within the coexistence window")
