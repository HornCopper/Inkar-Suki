"""Leaderboard scores for two successful Tian Chengsi sword rounds."""

from typing import Any

from src.const.jx3.kungfu import Kungfu
from src.utils.database import rank_db as db
from src.utils.database.classes import TCSRank


def _tcs_rank_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return 0


def build_tcs_rank_data(response: Any) -> list[dict[str, Any]]:
    if not isinstance(response, dict) or response.get("code") != 200:
        return []
    if response.get("rank_eligible") is not True:
        return []
    rounds = response.get("rounds")
    if not isinstance(rounds, list) or len(rounds) != 2:
        return []
    if any(not isinstance(record, dict) for record in rounds):
        return []
    if {_tcs_rank_int(record.get("order")) for record in rounds} != {1, 2}:
        return []
    if any(record.get("success") is not True or _tcs_rank_int(record.get("duration_ms")) <= 0 for record in rounds):
        return []
    for record in rounds:
        for metric in ("tank_healing", "sword_damage"):
            if not isinstance(record.get(metric), dict) or not isinstance(record[metric].get("players"), list):
                return []

    scores: dict[tuple[str, str, int], dict[str, Any]] = {}
    for record in rounds:
        duration_ms = _tcs_rank_int(record["duration_ms"])
        for metric, value_type in (("tank_healing", "health"), ("sword_damage", "damage")):
            for player in record[metric]["players"]:
                if not isinstance(player, dict):
                    continue
                kungfu_id = _tcs_rank_int(player.get("kungfu_id"))
                value = _tcs_rank_int(player.get("value"))
                if kungfu_id <= 0 or value <= 0:
                    continue
                healer = Kungfu.with_internel_id(kungfu_id).abbr == "N"
                if healer != (value_type == "health"):
                    continue
                role_name, separator, server_name = str(player.get("name") or "").rpartition("·")
                if not separator or not role_name or not server_name:
                    continue
                key = (role_name, server_name, kungfu_id)
                if key not in scores:
                    scores[key] = {
                        "role_name": role_name, "server_name": server_name, "kungfu_id": kungfu_id,
                        "total_damage": 0, "damage_per_second": 0, "total_health": 0, "health_per_second": 0,
                    }
                scores[key][f"total_{value_type}"] += value
                scores[key][f"{value_type}_per_second"] += value * 1000 // duration_ms
    return list(scores.values())


def save_tcs_rank_data(response: Any) -> int:
    scores = build_tcs_rank_data(response)
    if not scores:
        return 0
    inserted = 0
    with db.transaction():
        for score in scores:
            value_type = "health" if Kungfu.with_internel_id(score["kungfu_id"]).abbr == "N" else "damage"
            current = db.where_one(
                TCSRank(),
                f"role_name = ? AND server_name = ? AND kungfu_id = ? AND total_{value_type} = ? AND {value_type}_per_second = ?",
                score["role_name"], score["server_name"], score["kungfu_id"],
                score[f"total_{value_type}"], score[f"{value_type}_per_second"],
                default = None,
            )
            if current is None:
                db.save(TCSRank(**score))
                inserted += 1
    return inserted


def get_tcs_rank_records(kungfu_id: int = 0, ascending: bool = False) -> list[TCSRank]:
    value_type = "health" if Kungfu.with_internel_id(kungfu_id).abbr == "N" else "damage"
    records = db.where_all(TCSRank(), f"total_{value_type} > 0", default = [])
    selected = []
    for record in records:
        healer = Kungfu.with_internel_id(record.kungfu_id).abbr == "N"
        if healer != (value_type == "health"):
            continue
        if record.damage_per_second < 0 or record.health_per_second < 0:
            continue
        if kungfu_id and record.kungfu_id != kungfu_id:
            if not (kungfu_id in (10144, 10145) and record.kungfu_id in (10144, 10145)):
                continue
        selected.append(record)
    selected.sort(key = lambda record: getattr(record, f"{value_type}_per_second"), reverse = not ascending)
    if not ascending:
        counts: dict[tuple[str, str], int] = {}
        limited = []
        for record in selected:
            key = (record.server_name, record.role_name)
            if counts.get(key, 0) >= 3:
                continue
            counts[key] = counts.get(key, 0) + 1
            limited.append(record)
        selected = limited
    return selected[:20]
