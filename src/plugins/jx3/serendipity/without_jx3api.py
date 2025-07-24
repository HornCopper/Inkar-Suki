from typing import Any

from src.const.path import ASSETS, build_path
from src.const.jx3.server import Server
from src.utils.analyze import sort_dict_list, merge_dict_lists
from src.utils.network import Request
from src.utils.database import serendipity_db
from src.utils.database.classes import SerendipityData
from src.utils.database.player import search_player

import httpx
import os

class JX3Serendipity:
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

    async def get_tuilan_data(self, server: str, name: str):
        role = await search_player(role_name=name, server_name=server)
        global_role_id = role.globalRoleId
        if global_role_id == "":
            return False
        params = {
            "name": "完成奇遇",
            "gameRoleId": global_role_id,
            "size": 200
        }
        tl_data = (await Request("https://m.pvp.xoyo.com/achievement/list/achievements", params=params).post(tuilan=True)).json()
        serendipities = []
        for serendipity in tl_data["data"]["data"]:
            if serendipity["isFinished"]:
                serendipity_name = serendipity["name"]
                serendipity_level = self.get_serendipity_level(serendipity_name)
                if serendipity_level == 3:
                    serendipity_name = serendipity_name.replace("宠物奇缘·", "")
                serendipities.append(
                    {
                        "name": serendipity_name,
                        "level": serendipity_level,
                        "time": 0
                    }
                )
        self.tl = serendipities

    async def get_my_data(self, server: str, name: str):
        final_url = f"https://pull.j3cx.com/api/serendipity?server={server}&role={name}&pageSize=50"
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
            serendipity_level = self.get_serendipity_level(serendipity_name)
            new = {
                "name": serendipity_name,
                "level": serendipity_level,
                "time": serendipity["time"]
            }
            serendipities.append(new)
        self.my = serendipities

    async def get_jx3mm_data(self, server: str, name: str):
        final_url = f"https://www.jx3mm.com/home/qyinfo?m=1&R={Server(server).zone}&S={server}&t=&u=&n={name}"
        data = (await Request(final_url).get()).json()
        serendipities = []
        for serendipity in data["result"]:
            serendipities.append(
                {
                    "name": serendipity["serendipity"],
                    "level": self.get_serendipity_level(serendipity["serendipity"]),
                    "time": serendipity["time"]
                }
            )
        self.jx3mm = serendipities

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

    async def integration(self, server: str, name: str, uid: str) -> list[dict]:
        await self.get_tuilan_data(server, name)
        await self.get_my_data(server, name)
        await self.get_jx3mm_data(server, name)
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
        local_names = [data.serendipityName for data in local_data]
        if len(local_data) > 0:
            if local_data[0].roleName != name: # player name changed
                for data in local_data:
                    data.roleName = name
                    serendipity_db.save(data)
        for tp_serendipity in remote_data:
            if tp_serendipity["name"] in local_names:
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