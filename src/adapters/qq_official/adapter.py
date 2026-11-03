import asyncio
import hashlib
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from nonebot.adapters.qq import Adapter as QQAdapter, Bot
from nonebot.adapters.qq.config import BotInfo
from nonebot.adapters.qq.event import Event
from nonebot.adapters.qq.models import Dispatch

from src.const.path import DATA
from .lease import websocket_lease

_forward_tasks: ContextVar[set[asyncio.Task] | None] = ContextVar("qq_official_forward_tasks", default = None)
WEBSOCKET_LEASE_RETRY = 3


class Adapter(QQAdapter):
    async def run_bot_websocket(self, bot_info: BotInfo) -> None:
        shard = bot_info.shard[0] if bot_info.shard else 0
        key = hashlib.sha256(f"{bot_info.id}:{shard}".encode()).hexdigest()[:24]
        path = Path(DATA) / f"qq_official_ws_{key}.lock"
        while True:
            with websocket_lease(path) as acquired:
                if acquired:
                    tasks: set[asyncio.Task] = set()
                    token = _forward_tasks.set(tasks)
                    try:
                        # 获取凭证和网关也必须在进程锁内，避免多个工作进程并发登录。
                        await super().run_bot_websocket(bot_info)
                        # SDK 创建连接子任务后即返回；等待它们启动并登记，再持锁等待退出。
                        await asyncio.sleep(0)
                        if tasks:
                            await asyncio.gather(*tasks)
                    finally:
                        for task in tasks:
                            if not task.done():
                                task.cancel()
                        await asyncio.gather(*tasks, return_exceptions = True)
                        _forward_tasks.reset(token)
            await asyncio.sleep(WEBSOCKET_LEASE_RETRY)

    async def _forward_ws(self, bot: Bot, ws_url: Any, shard: tuple[int, int]) -> None:
        if (tasks := _forward_tasks.get()) is not None:
            task = asyncio.current_task()
            if task is not None:
                tasks.add(task)
        await super()._forward_ws(bot, ws_url, shard)

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
