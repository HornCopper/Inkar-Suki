from typing import Any
from pathlib import Path

from src.const.path import ASSETS, build_path
from src.const.jx3.server import Server
from src.utils.analyze import sort_dict_list, merge_dict_lists
from src.utils.network import Request
from src.utils.database import serendipity_db
from src.utils.database.classes import SerendipityData
from src.utils.database.player import search_player
from src.plugins.jx3.detail.detail import (
    ACHIEVEMENT_API,
    load_achievement_table,
    parse_completed_ids,
)

import httpx
import os

class JX3Serendipity:
    SERENDIPITY_TYPES = ("common", "peerless", "pet")

    def __init__(self):
        self.tl = []
        self.my = []
        self.jx3mm = []

    def get_serendipity_level(self, serendipity_name: str) -> int:
        if serendipity_name.find("宠物奇缘") != -1:
            serendipity_level = 3
        elif serendipity_name in [serendipity[:-4] for serendipity in os.listdir(build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", "pet"], end_with_slash=True))]:
            serendipity_level = 3
        elif serendipity_name in [serendipity[:-4] for serendipity in os.listdir(build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", "peerless"], end_with_slash=True))]:
            serendipity_level = 2
        else:
            serendipity_level = 1
        return serendipity_level

    def is_serendipity(self, name: str) -> bool:
        """Return whether *name* exists in the local serendipity catalogue."""
        base = Path(build_path(
            ASSETS,
            ["image", "jx3", "serendipity", "serendipity"],
            end_with_slash=True,
        ))
        return any((base / category / f"{name}.png").is_file() for category in self.SERENDIPITY_TYPES)

    async def get_my_data(self, server: str, name: str):
        final_url = f"https://pull-gplugin.jx3box.com/api/serendipity?server={server}&role={name}&pageSize=50"
        try:
            data = (await Request(final_url).get(timeout=3)).json()
        except httpx.ConnectTimeout:
            self.my = []
            return
        serendipities = []
        data = data["data"]["data"]
        if data is None:
            self.my = serendipities
            return
        for serendipity in data:
            serendipity_name = serendipity["serendipity"]
            # JX3Box's endpoint also returns other character events/items.  Only
            # merge entries present in our serendipity catalogue.
            if not self.is_serendipity(serendipity_name):
                continue
            serendipity_level = self.get_serendipity_level(serendipity_name)
            new = {
                "name": serendipity_name,
                "level": serendipity_level,
                "time": serendipity["time"]
            }
            serendipities.append(new)
        self.my = serendipities

    async def get_achievement_data(self, global_role_id: str) -> None:
        """Supplement completed serendipities from achievement IDs.

        Achievement records do not contain trigger timestamps, so supplemented
        entries deliberately use ``time=0`` (rendered as "遗忘的时间").
        """
        if not global_role_id:
            self.tl = []
            return
        try:
            response = await Request(
                ACHIEVEMENT_API,
                params={"jx3id": global_role_id},
            ).get(timeout=20)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError):
            self.tl = []
            return
        if payload.get("code") != 0 or not isinstance(payload.get("data"), dict):
            self.tl = []
            return

        completed_ids = parse_completed_ids(payload["data"].get("achievements"))
        supplemented: list[dict] = []
        handled_names: set[str] = set()
        for achievement in load_achievement_table():
            if achievement["id"] not in completed_ids:
                continue
            if "完成奇遇《" not in achievement["short_desc"]:
                continue
            serendipity_name = achievement["name"]
            if serendipity_name.startswith("宠物奇缘·"):
                serendipity_name = serendipity_name.removeprefix("宠物奇缘·")
            if (
                serendipity_name in handled_names
                or not self.is_serendipity(serendipity_name)
            ):
                continue
            handled_names.add(serendipity_name)
            supplemented.append(
                {
                    "name": serendipity_name,
                    "level": self.get_serendipity_level(serendipity_name),
                    "time": 0,
                }
            )
        self.tl = supplemented

    async def merge_api_with_my_data(
        self,
        api_data: list[dict],
        server: str,
        name: str,
        global_role_id: str = "",
        role_id: str = "",
    ) -> list[dict]:
        """Supplement JX3API records with community and achievement data."""
        await self.get_my_data(server, name)
        await self.get_achievement_data(global_role_id)
        merged = {
            item["event"]: item.copy()
            for item in api_data
            if item.get("event")
        }
        for item in self.my:
            if item["name"] not in merged:
                merged[item["name"]] = {
                    "event": item["name"],
                    "level": item["level"],
                    "time": item["time"],
                }
        for item in self.tl:
            if item["name"] not in merged:
                merged[item["name"]] = {
                    "event": item["name"],
                    "level": item["level"],
                    "time": 0,
                }
        result = sort_dict_list(list(merged.values()), "time")[::-1]
        if role_id:
            local_data: list[SerendipityData] | Any = serendipity_db.where_all(
                SerendipityData(),
                "server = ? AND roleId = ?",
                server,
                role_id,
                default=[],
            )
            self.save(
                local_data,
                [
                    {
                        "name": item.get("event") or item.get("name"),
                        "level": int(item.get("level") or 1),
                        "time": int(item.get("time") or 0),
                    }
                    for item in result
                    if item.get("event") or item.get("name")
                ],
                name,
                server,
                role_id,
            )
        return result

    def get_local_data(self, local_data: list[SerendipityData]) -> list[dict[str, int | str]]:
        result = []
        for data in local_data:
            result.append(
                {
                    "name": data.serendipityName,
                    "level": data.level,
                    "time": data.time
                }
            )
        return result

    async def integration(
        self,
        server: str,
        name: str,
        uid: str,
        global_role_id: str = "",
    ) -> list[dict]:
        await self.get_my_data(server, name)
        await self.get_achievement_data(global_role_id)
        final_data = sort_dict_list(
            merge_dict_lists(
                merge_dict_lists(
                    self.tl, 
                    self.my
                ),
                self.jx3mm
            ),
            "time"
        )[::-1]
        local_data: list[SerendipityData] | Any = serendipity_db.where_all(SerendipityData(), "server = ? AND roleId = ?", server, uid, default=[])
        local_data_dict = self.get_local_data(local_data)
        self.save(local_data, final_data, name, server, uid)
        return merge_dict_lists(final_data, local_data_dict)

    @staticmethod
    def save(local_data: list[SerendipityData], remote_data: list[dict], name: str, server: str, uid: str, /):
        local_by_name = {data.serendipityName: data for data in local_data}
        if len(local_data) > 0:
            if local_data[0].roleName != name: # player name changed
                for data in local_data:
                    data.roleName = name
                    serendipity_db.save(data)
        for tp_serendipity in remote_data:
            existing = local_by_name.get(tp_serendipity["name"])
            if existing:
                remote_time = int(tp_serendipity.get("time") or 0)
                if remote_time > existing.time:
                    existing.time = remote_time
                    existing.level = int(tp_serendipity.get("level") or existing.level)
                    serendipity_db.save(existing)
                continue
            else:
                serendipity_db.save(
                    SerendipityData(
                        roleName=name,
                        roleId=uid,
                        level=tp_serendipity["level"],
                        server=server,
                        serendipityName=tp_serendipity["name"],
                        time=tp_serendipity["time"]
                    )
                )
