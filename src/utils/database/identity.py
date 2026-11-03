"""将官方身份的数据归并到 QQ 号码；映射和数据库迁移一起提交。"""

import pickle
import re
import time
from contextlib import ExitStack
from dataclasses import dataclass
from typing import Any, Sequence

from src.utils.identity import IdentityScope, IdentityStore, get_identity_store
from .classes import Account, BannedUser, BanRecord, GroupMessage, GroupSettings, PersonalSettings, RaidTeamHealth
from .lib import Database

MATCH_PERMISSION = "manage.identity.bind"
ID_HELP = "格式：匹配个人 -内部ID QQ号，或 匹配群 -内部ID 群号"

# 仅迁移身份字段，角色 ID、奖品 ID、时间戳等数值不参与号码替换。
USER_FIELDS = {
    "user_id", "creator_id", "provider_id", "delivered_by", "invitor", "target_id",
    "uin_1", "uin_2", "operator_id", "submitter_id", "submit_id", "creator",
    "apply",
}
GROUP_FIELDS = {"group_id"}


def parse_match_ids(source: str, target: str) -> tuple[IdentityScope, int, int]:
    if not re.fullmatch(r"[ug]-[0-9]+", source) or not re.fullmatch(r"[ug][0-9]+", target):
        raise ValueError(ID_HELP)
    if source[0] != target[0]:
        raise ValueError("用户只能匹配用户，群只能匹配群。")
    source_id, target_id = int(source[1:]), int(target[1:])
    if not -(1 << 63) <= source_id < 0 or not 0 < target_id < (1 << 63):
        raise ValueError("ID 必须是有效的非零整数，左侧为负数，右侧为正数。")
    return ("user" if source[0] == "u" else "group"), source_id, target_id


def _semantic(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _semantic(item) for key, item in value.items() if key != "id"}
    if isinstance(value, list):
        return [_semantic(item) for item in value]
    return value


def _score(value: Any, default: Any = None) -> int:
    """有效数据量：非默认标量数、列表项目数及嵌套有效字段数。"""
    if value == default or value in (None, "", 0, False):
        return 0
    if isinstance(value, dict):
        defaults = default if isinstance(default, dict) else {}
        return sum(_score(item, defaults.get(key)) for key, item in value.items() if key not in {"id", "user_id", "group_id"})
    if isinstance(value, (list, tuple, set)):
        return sum(max(1, _score(item)) for item in value)
    return 1


def _merge(preferred: Any, other: Any, default: Any = None, field: str = "") -> Any:
    if isinstance(preferred, dict) and isinstance(other, dict):
        defaults = default if isinstance(default, dict) else {}
        return {
            key: _merge(preferred.get(key), other.get(key), defaults.get(key), key)
            for key in dict.fromkeys([*preferred, *other])
        }
    if isinstance(preferred, list) and isinstance(other, list):
        merged, keys = [], []
        for item in [*preferred, *other]:
            if field == "roles" and isinstance(item, dict):
                key = tuple(item.get(name) for name in ("serverName", "roleName", "roleId", "globalRoleId"))
            else:
                key = _semantic(item)
            if key not in keys:
                keys.append(key)
                merged.append(item)
        return merged
    if field in {"coins", "checkin_counts", "last_checkin"}:
        return max(item for item in (preferred, other) if item is not None)
    if field == "expire":
        values = [item for item in (preferred, other) if item is not None]
        return -1 if -1 in values else max(values)
    if preferred is None or preferred == default:
        return other if other is not None else preferred
    return preferred


def _replace_reference(value: Any, source: int, target: int) -> Any:
    if isinstance(value, (int, str)) and str(value) == str(source):
        return str(target) if isinstance(value, str) else target
    return value


def _rewrite(value: Any, scope: IdentityScope, source: int, target: int, field: str = "") -> Any:
    if isinstance(value, bytes):
        decoded = pickle.loads(value)
        rewritten = _rewrite(decoded, scope, source, target, field)
        return value if rewritten == decoded else pickle.dumps(rewritten)
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            name = key.removeprefix(Database.BYTES_PREFIX)
            if name == "delivered_target":
                result[key] = _replace_reference(item, source, target) if value.get("permission_scope") == scope else item
            elif field == "blacklist" and name == "source" and scope == "user":
                result[key] = _replace_reference(item, source, target)
            else:
                result[key] = _rewrite(item, scope, source, target, name)
        return result
    if isinstance(value, (list, tuple)):
        return type(value)(_rewrite(item, scope, source, target, field) for item in value)
    fields = USER_FIELDS | {"approver_user_ids"} if scope == "user" else GROUP_FIELDS
    return _replace_reference(value, source, target) if field in fields else value


@dataclass(frozen = True)
class MatchResult:
    scope: IdentityScope
    source_id: int
    target_id: int
    changed_rows: int = 0
    already_matched: bool = False


class IdentityMatcher:
    def __init__(self, identities: IdentityStore, database: Database, related: Sequence[Database] = ()):
        self.identities = identities
        self.database = database
        self.databases = list(dict.fromkeys([database, *related]))

    def match(self, source: str, target: str, operator_id: int) -> MatchResult:
        scope, source_id, target_id = parse_match_ids(source, target)
        with ExitStack() as stack:
            # 与正在执行的签到、奖品兑付等事务互斥，避免迁移时留下半份数据。
            for database in self.databases:
                stack.enter_context(database._lock)
                if database._transaction_depth:
                    raise RuntimeError("请在当前数据库事务结束后再匹配身份。")
            conn = self.database.conn
            attached = []
            try:
                conn.execute("ATTACH DATABASE ? AS identity_map", (str(self.identities.path.resolve()),))
                attached.append("identity_map")
                schemas = [("main", self.database)]
                for index, database in enumerate(self.databases[1:]):
                    schema = f"identity_data_{index}"
                    conn.execute(f"ATTACH DATABASE ? AS {schema}", (database.db_name,))
                    attached.append(schema)
                    schemas.append((schema, database))
                with self.database.transaction():
                    return self._match(conn, schemas, scope, source_id, target_id, operator_id)
            finally:
                for schema in reversed(attached):
                    conn.execute(f"DETACH DATABASE {schema}")

    def _match(self, conn, schemas, scope, source, target, operator):
        existing = conn.execute(
            "SELECT target_id FROM identity_map.identity_bindings WHERE scope = ? AND source_id = ?", (scope, source),
        ).fetchone()
        if existing:
            if existing[0] != target:
                raise ValueError(f"该内部 ID 已匹配到 {existing[0]}，不能改绑到其他号码。")
            return MatchResult(scope, source, target, already_matched = True)
        identity = conn.execute("SELECT scope FROM identity_map.identities WHERE id = ?", (source,)).fetchone()
        valid = identity and (
            identity[0] == "group" if scope == "group"
            else identity[0] == "user" or identity[0].startswith("member:")
        )
        if not valid:
            raise ValueError("找不到对应类型的官方身份，请先让该用户在目标群发送“官号信息”。")

        snapshots = []
        models = (Account, PersonalSettings, BannedUser) if scope == "user" else (GroupSettings,)
        for model_type in models:
            self._merge_profile(conn, model_type, scope, source, target, snapshots)
        changed = len(snapshots)
        for schema, database in schemas:
            changed += self._rewrite_tables(conn, schema, database, scope, source, target, snapshots)
        now = int(time.time())
        conn.execute(
            "INSERT INTO identity_map.identity_merge_history(scope, source_id, target_id, operator_id, created_at, snapshot) "
            "VALUES (?, ?, ?, ?, ?, ?)", (scope, source, target, operator, now, pickle.dumps(snapshots)),
        )
        conn.execute(
            "INSERT INTO identity_map.identity_bindings VALUES (?, ?, ?, ?, ?)", (scope, source, target, operator, now),
        )
        return MatchResult(scope, source, target, changed_rows = changed)

    def _merge_profile(self, conn, model_type, scope, source, target, snapshots):
        model = model_type()
        table, identity_field = model.TABLE_NAME, "user_id" if scope == "user" else "group_id"
        cursor = conn.execute(f'SELECT * FROM "{table}" WHERE "{identity_field}" IN (?, ?) ORDER BY id', (source, target))
        fields = [field[0] for field in cursor.description]
        raw_rows = [dict(zip(fields, row)) for row in cursor.fetchall()]
        if not raw_rows:
            return
        rows = [self.database._load(row) for row in raw_rows]
        defaults = model.dump()
        # 同分时保留真实号码侧；同一侧已有重复记录时优先保留较早的主记录。
        rows.sort(key = lambda row: (_score(row, defaults), str(row[identity_field]) == str(target), -row["id"]), reverse = True)
        merged = rows[0]
        for row in rows[1:]:
            merged = _merge(merged, row, defaults)
        merged[identity_field] = str(target) if scope == "group" else target
        merged["id"] = next((row["id"] for row in rows if str(row[identity_field]) == str(target)), merged["id"])
        snapshots.extend(("main", table, row) for row in raw_rows)
        conn.execute(f'DELETE FROM "{table}" WHERE "{identity_field}" IN (?, ?)', (source, target))
        self.database.save(model_type(**merged))

    def _rewrite_tables(self, conn, schema, database, scope, source, target, snapshots):
        changed = 0
        tables = conn.execute(f"SELECT name FROM {schema}.sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'").fetchall()
        for (table,) in tables:
            # 表名来自 SQLite schema；双引号转义后用作标识符。
            quoted = '"' + table.replace('"', '""') + '"'
            fields = [row[1] for row in conn.execute(f"PRAGMA {schema}.table_info({quoted})")]
            if not (set(fields) & (USER_FIELDS | GROUP_FIELDS | {"delivered_target"})):
                continue
            identity_fields = set(fields) & (USER_FIELDS if scope == "user" else GROUP_FIELDS)
            conditions = [f'"{field}" = ?' for field in sorted(identity_fields)]
            parameters = [source] * len(conditions)
            if "delivered_target" in fields:
                conditions.append("(delivered_target = ? AND permission_scope = ?)")
                parameters.extend([source, scope])
            embedded_fields = {"settings": {"blacklist", "opening"}, "raid_team_health": {"members"}}
            if scope == "user":
                for field in embedded_fields.get(table, set()):
                    column = Database.BYTES_PREFIX + field
                    if column in fields:
                        conditions.append(f'"{column}" IS NOT NULL')
            if not conditions:
                continue
            cursor = conn.execute(f"SELECT * FROM {schema}.{quoted} WHERE " + " OR ".join(conditions), parameters)
            rewritten_ids = set()
            for row in cursor.fetchall():
                original = dict(zip(fields, row))
                updated = _rewrite(original, scope, source, target)
                if updated == original:
                    continue
                snapshots.append((schema, table, original))
                columns = [field for field in fields if field != "id" and updated[field] != original[field]]
                assignments = ", ".join('"' + field.replace('"', '""') + '" = ?' for field in columns)
                conn.execute(f"UPDATE {schema}.{quoted} SET {assignments} WHERE id = ?", [*(updated[field] for field in columns), original["id"]])
                rewritten_ids.add(original["id"])
                changed += 1
            keyed_models = {
                "group_message": (GroupMessage, ("group_id", "user_id")),
                "ban_record": (BanRecord, ("group_id", "user_id")),
                "raid_team_health": (RaidTeamHealth, ("creator_id", "team_name")),
            }
            if table in keyed_models and identity_fields:
                model_type, keys = keyed_models[table]
                changed += self._coalesce(
                    conn, schema, database, model_type, keys, identity_fields, target, rewritten_ids, snapshots,
                )
            # 独立奖品的记录编号代表实物资产，保留全部；其他历史只去除内容完全相同的重复项。
            if table in {"random_affection_record", "affections", "equip_replacement_log", "random_image_record"}:
                columns = ", ".join('"' + field.replace('"', '""') + '"' for field in fields if field != "id")
                identity_fields = set(fields) & (USER_FIELDS if scope == "user" else GROUP_FIELDS)
                if not identity_fields:
                    continue
                target_filter = " OR ".join(f'"{field}" = ?' for field in sorted(identity_fields))
                cursor = conn.execute(
                    f"SELECT * FROM {schema}.{quoted} WHERE ({target_filter}) "
                    f"AND id NOT IN (SELECT MIN(id) FROM {schema}.{quoted} GROUP BY {columns})",
                    [target] * len(identity_fields),
                )
                for row in cursor.fetchall():
                    original = dict(zip(fields, row))
                    snapshots.append((schema, table, original))
                    conn.execute(f"DELETE FROM {schema}.{quoted} WHERE id = ?", (original["id"],))
                    changed += 1
        return changed

    def _coalesce(self, conn, schema, database, model_type, keys, identity_fields, target, rewritten_ids, snapshots):
        """把归并后拥有相同业务键的记录合成一条，避免 where_one 只读到其中一份。"""
        table = model_type.TABLE_NAME
        condition = " OR ".join(f'"{field}" = ?' for field in sorted(identity_fields))
        cursor = conn.execute(f'SELECT * FROM {schema}."{table}" WHERE {condition}', [target] * len(identity_fields))
        fields = [field[0] for field in cursor.description]
        groups = {}
        for raw in cursor.fetchall():
            row = dict(zip(fields, raw))
            groups.setdefault(tuple(row[key] for key in keys), []).append(row)
        changed = 0
        defaults = model_type().dump()
        for raw_rows in groups.values():
            if len(raw_rows) < 2:
                continue
            rows = [database._load(row) for row in raw_rows]
            rows.sort(key = lambda row: (_score(row, defaults), row["id"] not in rewritten_ids, -row["id"]), reverse = True)
            merged = rows[0]
            for row in rows[1:]:
                merged = _merge(merged, row, defaults)
            snapshots.extend((schema, table, row) for row in raw_rows)
            encoded = {}
            for field, value in merged.items():
                if field != "id":
                    encoded[database._get_stored_field_prefix(value) + field] = database._save(value) if isinstance(value, database.ITERABLE_TYPE) else value
            assignments = ", ".join(f'"{field}" = ?' for field in encoded)
            conn.execute(f'UPDATE {schema}."{table}" SET {assignments} WHERE id = ?', [*encoded.values(), merged["id"]])
            for row in rows:
                if row["id"] != merged["id"]:
                    conn.execute(f'DELETE FROM {schema}."{table}" WHERE id = ?', (row["id"],))
            changed += len(raw_rows)
        return changed


def match_identity(source: str, target: str, operator_id: int) -> MatchResult:
    from src.utils.database import cache_db, db, logs_db

    return IdentityMatcher(get_identity_store(), db, [cache_db, logs_db]).match(source, target, operator_id)
