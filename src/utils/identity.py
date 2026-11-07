"""官方 OpenID 的稳定内部标识，以及用户、群分别保存的号码映射。"""

import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from functools import cache
from pathlib import Path
from typing import Iterator, Literal
from urllib.parse import quote

IdentityScope = Literal["user", "group"]


class IdentityStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents = True, exist_ok = True)
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS identities ("
                "id INTEGER PRIMARY KEY, app_id TEXT NOT NULL, scope TEXT NOT NULL, openid TEXT NOT NULL, "
                "UNIQUE(app_id, scope, openid))",
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS incoming ("
                "app_id TEXT NOT NULL, session TEXT NOT NULL, message_id TEXT NOT NULL, received REAL NOT NULL, "
                "PRIMARY KEY(app_id, session, message_id))",
            )
            conn.execute("CREATE INDEX IF NOT EXISTS incoming_received ON incoming(received)")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS identity_bindings ("
                "scope TEXT NOT NULL, source_id INTEGER NOT NULL, target_id INTEGER NOT NULL, "
                "operator_id INTEGER NOT NULL, created_at INTEGER NOT NULL, PRIMARY KEY(scope, source_id))",
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS identity_merge_history ("
                "id INTEGER PRIMARY KEY, scope TEXT NOT NULL, source_id INTEGER NOT NULL, target_id INTEGER NOT NULL, "
                "operator_id INTEGER NOT NULL, created_at INTEGER NOT NULL, snapshot BLOB NOT NULL)",
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS qq_group_delivery ("
                "app_id TEXT NOT NULL, openid TEXT NOT NULL, joined INTEGER NOT NULL DEFAULT 1, "
                "joined_at REAL NOT NULL DEFAULT 0, allowed INTEGER, allowed_at REAL NOT NULL DEFAULT 0, "
                "PRIMARY KEY(app_id, openid))",
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS qq_push_attempts ("
                "app_id TEXT NOT NULL, openid TEXT NOT NULL, fingerprint TEXT NOT NULL, attempted REAL NOT NULL)",
            )
            conn.execute("CREATE INDEX IF NOT EXISTS qq_push_attempted ON qq_push_attempts(app_id, attempted)")
            conn.execute("CREATE INDEX IF NOT EXISTS qq_push_target ON qq_push_attempts(app_id, openid, attempted)")

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path, timeout = 5)
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def identify(self, app_id: str, scope: str, openid: str) -> int:
        key = (app_id, scope, openid)
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id FROM identities WHERE app_id = ? AND scope = ? AND openid = ?", key,
            ).fetchone()
            if row:
                return row[0]
            seed = json.dumps(key, ensure_ascii = True).encode()
            for salt in range(100):
                digest = hashlib.sha256(seed + str(salt).encode()).digest()
                internal_id = -(int.from_bytes(digest[:8], "big") % ((1 << 62) - 1) + 1)
                conn.execute("INSERT OR IGNORE INTO identities VALUES (?, ?, ?, ?)", (internal_id, *key))
                row = conn.execute(
                    "SELECT id FROM identities WHERE app_id = ? AND scope = ? AND openid = ?", key,
                ).fetchone()
                if row:
                    return row[0]
        raise RuntimeError("QQ OpenID 内部 ID 分配失败")

    def resolve(self, scope: IdentityScope, identity: int | str) -> int:
        identity = int(identity)
        if identity >= 0:
            return identity
        with self.connect() as conn:
            row = conn.execute(
                "SELECT target_id FROM identity_bindings WHERE scope = ? AND source_id = ?", (scope, identity),
            ).fetchone()
        return row[0] if row else identity

    def known(self, app_id: str, scope: str) -> list[tuple[int, str]]:
        """仅返回本地实际见过的身份，不代表平台的完整群或好友名单。"""
        binding_scope = "group" if scope == "group" else "user"
        with self.connect() as conn:
            return conn.execute(
                "SELECT COALESCE(b.target_id, i.id), i.openid FROM identities i "
                "LEFT JOIN identity_bindings b ON b.source_id = i.id AND b.scope = ? "
                "WHERE i.app_id = ? AND i.scope = ? ORDER BY i.id",
                (binding_scope, app_id, scope),
            ).fetchall()

    def lookup(self, app_id: str, scope: str, identity: int | str) -> str | None:
        """反查同一应用、同一群成员作用域内的 OpenID，接受匹配前后的 ID。"""
        value = int(identity)
        expected = self.resolve("group" if scope == "group" else "user", value)
        for canonical, openid in self.known(app_id, scope):
            if canonical == expected:
                return openid
        return None

    def user_avatar_url(self, identity: int | str) -> str | None:
        """仅为本地已记录的用户身份构造头像地址，不将群或消息身份当作用户。"""
        with self.connect() as conn:
            row = conn.execute(
                "SELECT app_id, openid FROM identities WHERE id = ? AND (scope = 'user' OR scope LIKE 'member:%')",
                (int(identity),),
            ).fetchone()
        if row is None:
            return None
        app_id, openid = (quote(value, safe = "") for value in row)
        return f"https://q.qlogo.cn/qqapp/{app_id}/{openid}/100"

    def claim_message(self, app_id: str, session: str, message_id: str) -> bool:
        now = time.time()
        with self.connect() as conn:
            conn.execute("DELETE FROM incoming WHERE received < ?", (now - 86400,))
            return conn.execute(
                "INSERT OR IGNORE INTO incoming VALUES (?, ?, ?, ?)", (app_id, session, message_id, now),
            ).rowcount == 1

    def observe_group(
        self, app_id: str, openid: str, *, joined: bool | None = None,
        allowed: bool | None = None, timestamp: float | None = None,
    ) -> None:
        """群消息只确认仍在群内，不能覆盖群主动消息开关；旧事件不能覆盖新状态。"""
        timestamp = time.time() if timestamp is None else timestamp
        with self.connect() as conn:
            conn.execute("INSERT OR IGNORE INTO qq_group_delivery(app_id, openid) VALUES (?, ?)", (app_id, openid))
            for column, value in (("joined", joined), ("allowed", allowed)):
                if value is not None:
                    conn.execute(
                        f"UPDATE qq_group_delivery SET {column} = ?, {column}_at = ? "
                        f"WHERE app_id = ? AND openid = ? AND {column}_at <= ?",
                        (int(value), timestamp, app_id, openid, timestamp),
                    )

    def group_delivery_block(self, app_id: str, openid: str) -> str | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT joined, allowed FROM qq_group_delivery WHERE app_id = ? AND openid = ?", (app_id, openid),
            ).fetchone()
        if row and not row[0]:
            return "机器人已退出该群"
        if row and row[1] == 0:
            return "群已关闭允许主动消息"
        # 老版本已记录的群可能没有状态事件，由官方发送接口最终校验权限。
        return None

    def reserve_push(self, app_id: str, openid: str, fingerprint: str, day_start: float) -> tuple[str, float]:
        """跨进程去重和限频；只保存内容摘要，不保存消息正文或图片。"""
        now = time.time()
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("DELETE FROM qq_push_attempts WHERE attempted < ?", (now - 2 * 86400,))
            duplicate = conn.execute(
                "SELECT 1 FROM qq_push_attempts WHERE app_id = ? AND openid = ? AND fingerprint = ? AND attempted > ?",
                (app_id, openid, fingerprint, now - 600),
            ).fetchone()
            if duplicate:
                return "duplicate", 0
            daily = conn.execute(
                "SELECT COUNT(*) FROM qq_push_attempts WHERE app_id = ? AND openid = ? AND attempted >= ?",
                (app_id, openid, day_start),
            ).fetchone()[0]
            if daily >= 1000:
                return "daily_limit", 0
            delay = 0.0
            # 使用未认证应用的保守额度：每应用 30/分钟，每群 20/分钟。
            for target, limit in ((False, 30), (True, 20)):
                where = "app_id = ? AND attempted > ?" + (" AND openid = ?" if target else "")
                args = (app_id, now - 60, openid) if target else (app_id, now - 60)
                count, earliest = conn.execute(f"SELECT COUNT(*), MIN(attempted) FROM qq_push_attempts WHERE {where}", args).fetchone()
                if count >= limit:
                    delay = max(delay, earliest + 60.01 - now)
            if delay > 0:
                return "wait", delay
            conn.execute("INSERT INTO qq_push_attempts VALUES (?, ?, ?, ?)", (app_id, openid, fingerprint, now))
            return "ready", 0


@cache
def get_identity_store() -> IdentityStore:
    from src.const.path import DATA

    return IdentityStore(Path(DATA) / "qq_official.sqlite3")


def resolve_user_id(user_id: int | str) -> int:
    value = int(user_id)
    return get_identity_store().resolve("user", value) if value < 0 else value


def resolve_group_id(group_id: int | str) -> int:
    value = int(group_id)
    return get_identity_store().resolve("group", value) if value < 0 else value
