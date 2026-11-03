"""官方 OpenID 的稳定内部标识，以及用户、群分别保存的号码映射。"""

import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from functools import cache
from pathlib import Path
from typing import Iterator, Literal

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

    def claim_message(self, app_id: str, session: str, message_id: str) -> bool:
        now = time.time()
        with self.connect() as conn:
            conn.execute("DELETE FROM incoming WHERE received < ?", (now - 86400,))
            return conn.execute(
                "INSERT OR IGNORE INTO incoming VALUES (?, ?, ?, ?)", (app_id, session, message_id, now),
            ).rowcount == 1


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
