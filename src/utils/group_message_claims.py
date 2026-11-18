"""同机多进程的短时群消息认领；仅保存分类摘要，不保存正文、文件信息或发送者。"""

from asyncio import sleep, to_thread
import hashlib
import time
import uuid
from typing import Literal

from .identity import IdentityStore
from .qq_official_config import QQCoexistenceConfig


class GroupMessageClaims:
    def __init__(self, identities: IdentityStore, config: QQCoexistenceConfig):
        self.identities = identities
        self.config = config
        with identities.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS qq_group_message_claims ("
                "group_id INTEGER NOT NULL, fingerprint TEXT NOT NULL, token TEXT NOT NULL, "
                "received REAL NOT NULL, owner TEXT, PRIMARY KEY(group_id, fingerprint))",
            )
            conn.execute("CREATE INDEX IF NOT EXISTS qq_group_claim_received ON qq_group_message_claims(received)")

    def has_official_group(self, group_id: int) -> bool:
        with self.identities.connect() as conn:
            return conn.execute(
                "SELECT 1 FROM identity_bindings b JOIN identities i ON i.id = b.source_id "
                "WHERE b.scope = 'group' AND i.scope = 'group' AND b.target_id = ? LIMIT 1",
                (group_id,),
            ).fetchone() is not None

    def offer(self, group_id: int, text: str, *, official: bool, kind: Literal["text", "file"] = "text") -> str | None:
        """返回本次认领令牌；官方先占位，OneBot 可在等待期间接手该占位。"""
        fingerprint = hashlib.sha256(f"{kind}\0{text}".encode("utf-8")).hexdigest()
        token = uuid.uuid4().hex
        with self.identities.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            # 在获得写锁后计时；重复消息不更新 received，窗口从首次入站起固定计算。
            now = time.time()
            conn.execute("DELETE FROM qq_group_message_claims WHERE received <= ?", (now - self.config.window_seconds,))
            row = conn.execute(
                "SELECT owner FROM qq_group_message_claims WHERE group_id = ? AND fingerprint = ?",
                (group_id, fingerprint),
            ).fetchone()
            if row is not None:
                if official or row[0] is not None:
                    return None
                conn.execute(
                    "UPDATE qq_group_message_claims SET owner = 'onebot', token = ? "
                    "WHERE group_id = ? AND fingerprint = ?", (token, group_id, fingerprint),
                )
            else:
                conn.execute(
                    "INSERT INTO qq_group_message_claims VALUES (?, ?, ?, ?, ?)",
                    (group_id, fingerprint, token, now, None if official else "onebot"),
                )
        return token

    def finish_official(self, token: str) -> bool:
        # 令牌同时区分新旧窗口，旧等待任务不能认领后来新建的同内容消息。
        with self.identities.connect() as conn:
            return conn.execute(
                "UPDATE qq_group_message_claims SET owner = 'official' WHERE token = ? AND owner IS NULL", (token,),
            ).rowcount == 1

    async def accept(self, group_id: int, text: str, *, official: bool, kind: Literal["text", "file"] = "text") -> bool:
        token = await to_thread(self.offer, group_id, text, official = official, kind = kind)
        if token is None:
            return False
        if not official:
            return True
        await sleep(self.config.official_wait_seconds)
        return await to_thread(self.finish_official, token)
