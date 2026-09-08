from __future__ import annotations

import asyncio
import hashlib
from typing import Any

from nonebot.log import logger

from src.config import Config
from src.utils.database import cache_db
from src.utils.database.classes import (
    EquipmentRatingRaceBossCache,
    EquipmentRatingRaceEventCache,
    EquipmentRatingRaceRoleCache,
)
from src.utils.network import Request
from src.utils.time import Time


FULL_BOSS_RANK_SIZE = 100
RACE_RANK_API_TIMEOUT = 20


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _race_rank_source_key() -> str:
    config = Config.jx3.race_rank
    raw = "\n".join(
        [
            str(config.cache_version),
            str(config.event_id),
            str(config.event_api),
            str(config.boss_rank_api),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _format_api_url(template: str, *, event_id: int, achievement_id: int = 0) -> str:
    return template.format(
        event_id=event_id,
        achievement_id=achievement_id,
        server="",
    )


def _normalize_boss_map(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    bosses: list[dict[str, Any]] = []
    seen: set[int] = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        achievement_id = _to_int(item.get("achievement_id"))
        if achievement_id <= 0 or achievement_id in seen:
            continue
        seen.add(achievement_id)
        bosses.append(
            {
                "achievement_id": achievement_id,
                "name": str(item.get("name") or achievement_id),
                "order": len(bosses),
            }
        )
    return bosses


def _event_cache(source_key: str, event_id: int) -> EquipmentRatingRaceEventCache | None:
    cached = cache_db.where_one(
        EquipmentRatingRaceEventCache(),
        "source_key = ? AND event_id = ?",
        source_key,
        event_id,
        default=None,
    )
    if not isinstance(cached, EquipmentRatingRaceEventCache):
        return None
    return cached if _normalize_boss_map(cached.boss_map) else None


def _save_event_cache(
    source_key: str,
    event_id: int,
    event_name: str,
    boss_map: list[dict[str, Any]],
) -> None:
    rows = cache_db.where_all(
        EquipmentRatingRaceEventCache(),
        "source_key = ? AND event_id = ?",
        source_key,
        event_id,
        default=[],
    ) or []
    valid_rows = [row for row in rows if isinstance(row, EquipmentRatingRaceEventCache)]
    current = valid_rows[0] if valid_rows else EquipmentRatingRaceEventCache()
    current.source_key = source_key
    current.event_id = event_id
    current.event_name = event_name
    current.boss_map = boss_map
    current.timestamp = Time().raw_time
    cache_db.save(current)
    for duplicate in valid_rows[1:]:
        if duplicate.id is not None:
            cache_db.delete(EquipmentRatingRaceEventCache(), "id = ?", duplicate.id)


async def _request_event(source_key: str, event_id: int) -> dict[str, Any] | None:
    config = Config.jx3.race_rank
    try:
        url = _format_api_url(str(config.event_api), event_id=event_id)
        response = await Request(url).get(timeout=RACE_RANK_API_TIMEOUT)
        if response.status_code >= 400:
            logger.warning(f"装备评级百强赛事查询失败：HTTP {response.status_code}")
            return None
        result = response.json()
    except Exception as exc:
        logger.warning(f"装备评级百强赛事查询失败：{exc}")
        return None
    if not isinstance(result, dict) or result.get("code") not in (0, 200, "0", "200"):
        logger.warning("装备评级百强赛事查询失败：接口返回失败状态")
        return None
    data = result.get("data")
    if not isinstance(data, dict):
        logger.warning("装备评级百强赛事查询失败：接口数据为空")
        return None
    boss_map = _normalize_boss_map(data.get("boss_map"))
    if not boss_map:
        logger.warning("装备评级百强赛事查询失败：赛事没有有效 boss_map")
        return None
    event_name = str(data.get("name") or "")
    _save_event_cache(source_key, event_id, event_name, boss_map)
    return {
        "event_id": event_id,
        "event_name": event_name,
        "boss_map": boss_map,
    }


async def _get_event(source_key: str, event_id: int) -> dict[str, Any] | None:
    cached = _event_cache(source_key, event_id)
    if cached is not None:
        return {
            "event_id": event_id,
            "event_name": cached.event_name,
            "boss_map": _normalize_boss_map(cached.boss_map),
        }
    return await _request_event(source_key, event_id)


def _boss_cache(
    source_key: str,
    event_id: int,
    achievement_id: int,
) -> list[dict[str, Any]] | None:
    cached = cache_db.where_one(
        EquipmentRatingRaceBossCache(),
        "source_key = ? AND event_id = ? AND achievement_id = ?",
        source_key,
        event_id,
        achievement_id,
        default=None,
    )
    if not isinstance(cached, EquipmentRatingRaceBossCache):
        return None
    records = [record for record in cached.records if isinstance(record, dict)]
    return records if len(records) >= FULL_BOSS_RANK_SIZE else None


def _save_boss_cache(
    source_key: str,
    event_id: int,
    boss: dict[str, Any],
    records: list[dict[str, Any]],
) -> None:
    achievement_id = _to_int(boss.get("achievement_id"))
    rows = cache_db.where_all(
        EquipmentRatingRaceBossCache(),
        "source_key = ? AND event_id = ? AND achievement_id = ?",
        source_key,
        event_id,
        achievement_id,
        default=[],
    ) or []
    valid_rows = [row for row in rows if isinstance(row, EquipmentRatingRaceBossCache)]
    current = valid_rows[0] if valid_rows else EquipmentRatingRaceBossCache()
    current.source_key = source_key
    current.event_id = event_id
    current.achievement_id = achievement_id
    current.boss_name = str(boss.get("name") or achievement_id)
    current.records = records
    current.timestamp = Time().raw_time
    cache_db.save(current)
    for duplicate in valid_rows[1:]:
        if duplicate.id is not None:
            cache_db.delete(EquipmentRatingRaceBossCache(), "id = ?", duplicate.id)


async def _request_boss_records(
    source_key: str,
    event_id: int,
    boss: dict[str, Any],
) -> tuple[list[dict[str, Any]] | None, bool]:
    achievement_id = _to_int(boss.get("achievement_id"))
    cached = _boss_cache(source_key, event_id, achievement_id)
    if cached is not None:
        return cached, True
    try:
        url = _format_api_url(
            str(Config.jx3.race_rank.boss_rank_api),
            event_id=event_id,
            achievement_id=achievement_id,
        )
        response = await Request(url).get(timeout=RACE_RANK_API_TIMEOUT)
        if response.status_code >= 400:
            logger.warning(f"装备评级百强 Boss {achievement_id} 查询失败：HTTP {response.status_code}")
            return None, False
        result = response.json()
    except Exception as exc:
        logger.warning(f"装备评级百强 Boss {achievement_id} 查询失败：{exc}")
        return None, False
    if not isinstance(result, dict) or result.get("code") not in (0, 200, "0", "200"):
        logger.warning(f"装备评级百强 Boss {achievement_id} 查询失败：接口返回失败状态")
        return None, False
    data = result.get("data")
    if not isinstance(data, list):
        logger.warning(f"装备评级百强 Boss {achievement_id} 查询失败：接口数据为空")
        return None, False
    records = [record for record in data if isinstance(record, dict)]
    is_full = len(records) >= FULL_BOSS_RANK_SIZE
    if is_full:
        _save_boss_cache(source_key, event_id, boss, records)
    return records, is_full


def _teammate_guids(value: Any) -> set[str]:
    if not isinstance(value, str):
        return set()
    guids: set[str] = set()
    for member in value.split(";"):
        fields = member.split(",", 3)
        member_guid = fields[2].strip() if len(fields) >= 3 else ""
        if member_guid.isdigit():
            guids.add(member_guid)
    return guids


def _record_has_guid(record: dict[str, Any], guid: str) -> bool:
    if str(record.get("guid") or "") == guid:
        return True
    return guid in _teammate_guids(record.get("teammate"))


def _find_role_results(
    records: list[dict[str, Any]],
    boss: dict[str, Any],
    guid: str,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    visible_rank = 0
    for record in records:
        if _to_int(record.get("superstar")) != 0:
            continue
        visible_rank += 1
        if not _record_has_guid(record, guid):
            continue
        results.append(
            {
                "achievement_id": _to_int(boss.get("achievement_id")),
                "boss_name": str(boss.get("name") or "未知首领"),
                "boss_order": _to_int(boss.get("order")),
                "rank": visible_rank,
                "created": _to_int(record.get("created")),
            }
        )
    return results


def _role_cache(
    source_key: str,
    event_id: int,
    guid: str,
) -> EquipmentRatingRaceRoleCache | None:
    cached = cache_db.where_one(
        EquipmentRatingRaceRoleCache(),
        "source_key = ? AND event_id = ? AND guid = ?",
        source_key,
        event_id,
        guid,
        default=None,
    )
    return cached if isinstance(cached, EquipmentRatingRaceRoleCache) else None


def _save_role_cache(
    source_key: str,
    event_id: int,
    guid: str,
    resolved_achievement_ids: set[int],
    results: list[dict[str, Any]],
) -> None:
    rows = cache_db.where_all(
        EquipmentRatingRaceRoleCache(),
        "source_key = ? AND event_id = ? AND guid = ?",
        source_key,
        event_id,
        guid,
        default=[],
    ) or []
    valid_rows = [row for row in rows if isinstance(row, EquipmentRatingRaceRoleCache)]
    current = valid_rows[0] if valid_rows else EquipmentRatingRaceRoleCache()
    current.source_key = source_key
    current.event_id = event_id
    current.guid = guid
    current.resolved_achievement_ids = sorted(resolved_achievement_ids)
    current.results = results
    current.timestamp = Time().raw_time
    cache_db.save(current)
    for duplicate in valid_rows[1:]:
        if duplicate.id is not None:
            cache_db.delete(EquipmentRatingRaceRoleCache(), "id = ?", duplicate.id)


def _normalize_role_results(
    value: Any,
    bosses: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    boss_by_id = {
        _to_int(boss.get("achievement_id")): boss
        for boss in bosses
    }
    results: dict[tuple[int, int, int], dict[str, Any]] = {}
    for item in value:
        if not isinstance(item, dict):
            continue
        achievement_id = _to_int(item.get("achievement_id"))
        rank = _to_int(item.get("rank"))
        boss = boss_by_id.get(achievement_id)
        if boss is None or rank <= 0:
            continue
        created = _to_int(item.get("created"))
        results[(achievement_id, rank, created)] = {
            "achievement_id": achievement_id,
            "boss_name": str(boss.get("name") or item.get("boss_name") or "未知首领"),
            "boss_order": _to_int(boss.get("order")),
            "rank": rank,
            "created": created,
        }
    return sorted(
        results.values(),
        key=lambda item: (item["boss_order"], item["rank"], item["created"]),
    )


def _prepare_race_rank_view(
    event_name: str,
    results: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not results:
        return None
    best_rank = min(item["rank"] for item in results)
    best = [item for item in results if item["rank"] == best_rank]
    latest = max(results, key=lambda item: (item["created"], item["boss_order"]))
    latest_key = (latest["achievement_id"], latest["rank"], latest["created"])
    latest_is_best = any(
        (item["achievement_id"], item["rank"], item["created"]) == latest_key
        for item in best
    )
    best_items = [
        {
            "boss_name": item["boss_name"],
            "rank": item["rank"],
            "is_latest": (
                item["achievement_id"],
                item["rank"],
                item["created"],
            ) == latest_key,
        }
        for item in best
    ]
    groups = [
        {
            "kind": "best",
            "label": "最佳 · 最新" if len(best_items) == 1 and latest_is_best else "最佳",
            "items": best_items,
            "mark_latest_item": len(best_items) > 1 and latest_is_best,
        }
    ]
    if not latest_is_best:
        groups.append(
            {
                "kind": "latest",
                "label": "最新",
                "items": [
                    {
                        "boss_name": latest["boss_name"],
                        "rank": latest["rank"],
                        "is_latest": True,
                    }
                ],
                "mark_latest_item": False,
            }
        )
    return {
        "event_name": event_name,
        "groups": groups,
    }


async def get_equipment_rating_race_rank(guid: int | str) -> dict[str, Any] | None:
    config = Config.jx3.race_rank
    fixed_guid = str(guid).strip()
    event_id = _to_int(config.event_id)
    if (
        not config.enabled
        or event_id <= 0
        or not fixed_guid.isdigit()
        or _to_int(fixed_guid) <= 0
        or not str(config.event_api).strip()
        or not str(config.boss_rank_api).strip()
    ):
        return None

    source_key = _race_rank_source_key()
    event = await _get_event(source_key, event_id)
    if event is None:
        return None
    bosses = event["boss_map"]
    boss_ids = {_to_int(boss.get("achievement_id")) for boss in bosses}

    cached_role = _role_cache(source_key, event_id, fixed_guid)
    resolved_ids = {
        _to_int(achievement_id)
        for achievement_id in (cached_role.resolved_achievement_ids if cached_role is not None else [])
        if _to_int(achievement_id) in boss_ids
    }
    cached_results = _normalize_role_results(
        cached_role.results if cached_role is not None else [],
        bosses,
    )
    results = list(cached_results)
    pending_bosses = [
        boss
        for boss in bosses
        if _to_int(boss.get("achievement_id")) not in resolved_ids
    ]
    if not pending_bosses:
        return _prepare_race_rank_view(str(event.get("event_name") or ""), cached_results)

    responses = await asyncio.gather(
        *[
            _request_boss_records(source_key, event_id, boss)
            for boss in pending_bosses
        ]
    )
    if any(records is None for records, _ in responses):
        return None

    for boss, (records, is_full) in zip(pending_bosses, responses):
        if records is None:
            return None
        achievement_id = _to_int(boss.get("achievement_id"))
        matched_results = _find_role_results(records, boss, fixed_guid)
        if matched_results:
            results.extend(matched_results)
            resolved_ids.add(achievement_id)
        elif is_full:
            resolved_ids.add(achievement_id)

    results = _normalize_role_results(results, bosses)
    _save_role_cache(source_key, event_id, fixed_guid, resolved_ids, results)
    return _prepare_race_rank_view(str(event.get("event_name") or ""), results)
