from copy import deepcopy
from typing import Any, TYPE_CHECKING, cast

from src.utils.jx3_data import get_item

import asyncio
import time

if TYPE_CHECKING:
    from httpx import Response

DungeonPayload = list[dict[str, Any]] | dict[str, Any] | None
CACHE_SECONDS = 300
_cache: dict[tuple[str, str], tuple[float, DungeonPayload]] = {}
_pending: dict[tuple[str, str], asyncio.Task[DungeonPayload]] = {}

def _base_url() -> str:
    from src.config import Config

    root = Config.jx3.api.calculator_url.strip().rstrip("/")
    if not root:
        raise ValueError("请配置 jx3.api.calculator_url 以访问副本掉落接口。")
    return root

async def _request(url: str) -> "Response":
    from src.utils.network import Request

    return await Request(url).get()

async def _fetch(key: tuple[str, str]) -> DungeonPayload:
    root, path = key
    response = await _request(root + path)
    if response.status_code == 404 and path != "/bot/dungeons":
        data = None
    else:
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data") if isinstance(payload, dict) else None
        if path == "/bot/dungeons":
            if not isinstance(data, list) or any(
                    not isinstance(row, dict)
                    or not {"id", "canonicalName", "name", "mode", "bosses", "requiredLevel"} <= row.keys()
                    for row in data):
                raise ValueError("Invalid dungeon catalogue response")
        elif (not isinstance(data, dict) or not isinstance(data.get("entries"), list)
              or not isinstance(data.get("bosses"), list) or str(data.get("id")) != path.rsplit("/", 1)[-1]):
            raise ValueError("Invalid dungeon drop response")
    _cache[key] = time.monotonic() + CACHE_SECONDS, data
    return data

def _finished(key: tuple[str, str], task: asyncio.Task[DungeonPayload]) -> None:
    if _pending.get(key) is task:
        _pending.pop(key)
    if not task.cancelled():
        task.exception()

async def _load(path: str) -> DungeonPayload:
    key = _base_url(), path
    cached = _cache.get(key)
    if cached and cached[0] > time.monotonic():
        return cached[1]
    task = _pending.get(key)
    if task is None:
        task = asyncio.create_task(_fetch(key))
        _pending[key] = task
        task.add_done_callback(lambda done: _finished(key, done))
    # 一个命令被取消时，不取消其他命令共用的请求。
    return await asyncio.shield(task)

async def dungeon_catalogue() -> dict[str, dict[str, Any]]:
    # _fetch 已按请求路径校验响应结构。
    records = cast(list[dict[str, Any]], await _load("/bot/dungeons"))
    return {str(row["id"]): deepcopy(row) for row in records}

async def find_dungeon(name: str, mode: str) -> dict[str, Any] | None:
    records = cast(list[dict[str, Any]], await _load("/bot/dungeons"))
    for row in records:
        if row["mode"] == mode and name in (row["canonicalName"], row["name"]):
            return deepcopy(row)
    return None

async def dungeon_by_id(map_id: int) -> dict[str, Any] | None:
    record = cast(dict[str, Any] | None, await _load(f"/bot/dungeons/{int(map_id)}"))
    return deepcopy(record)

async def dungeon_drops(map_id: int) -> dict[str, list[dict[str, Any]]]:
    record = await dungeon_by_id(map_id)
    if not record:
        return {}
    result = {name: [] for name in record["bosses"]}
    seen = set()
    for entry in record["entries"]:
        identity = entry["boss"], entry["key"]
        if identity in seen:
            continue
        seen.add(identity)
        row = get_item(entry["key"])
        if row is None:
            raise ValueError(f"本地掉落物品资料缺失：{entry['key']}")
        result.setdefault(entry["boss"], []).append(row)
    return result
