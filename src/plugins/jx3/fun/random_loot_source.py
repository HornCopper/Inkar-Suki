from typing import Any

from src.utils.jx3_dungeons import dungeon_by_id, dungeon_drops

async def get_lua_boss_items(map_id: int) -> dict[str, set[tuple[int, int]]]:
    record = await dungeon_by_id(map_id)
    if record is None:
        return {}
    result = {name: set() for name in record["bosses"]}
    for entry in record["entries"]:
        result.setdefault(entry["boss"], set()).add((entry["type"], entry["id"]))
    return result

async def get_local_lua_boss_drops(map_id: int) -> dict[str, list[dict[str, Any]]]:
    return await dungeon_drops(map_id)
