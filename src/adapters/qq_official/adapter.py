import asyncio
import hashlib
from pathlib import Path
from typing import Any

from nonebot.adapters.qq import Adapter as QQAdapter, Bot
from nonebot.adapters.qq.event import Event
from nonebot.adapters.qq.models import Dispatch
from nonebot.log import logger

from src.const.path import DATA
from .lease import websocket_lease


class Adapter(QQAdapter):
    async def _forward_ws(self, bot: Bot, ws_url: Any, shard: tuple[int, int]) -> None:
        key = hashlib.sha256(f"{bot.self_id}:{shard[0]}".encode()).hexdigest()[:24]
        path = Path(DATA) / f"qq_official_ws_{key}.lock"
        while True:
            with websocket_lease(path) as acquired:
                if acquired:
                    logger.info("QQ 官方 WebSocket 已取得分片进程锁")
                    await super()._forward_ws(bot, ws_url, shard)
                    return
            await asyncio.sleep(3)

    @staticmethod
    def payload_to_event(payload: Dispatch) -> Event:
        # 官方现行事件仅保证 group_openid；SDK 1.7.3 仍要求旧 group_id 字段。
        if payload.type in {"GROUP_AT_MESSAGE_CREATE", "GROUP_MESSAGE_CREATE", "C2C_MESSAGE_CREATE"}:
            data = dict(payload.data)
            author = dict(data.get("author", {}))
            group = payload.type != "C2C_MESSAGE_CREATE"
            key = "member_openid" if group else "user_openid"
            author.setdefault("id", author.get(key, ""))
            if group:
                data.setdefault("group_id", data.get("group_openid", ""))
                author.setdefault("bot", False)
                author.setdefault("member_role", "member")
            data["author"] = author
            # 本接入只处理正文和图片，不处理提及其他用户的操作。
            data["mentions"] = None
            payload = payload.model_copy(update = {"data": data})
        return QQAdapter.payload_to_event(payload)
