from src.const.path import ASSETS, build_path
from src.const.jx3.server import Server
from src.utils.analyze import sort_dict_list, merge_dict_lists
from src.utils.network import Request
from src.utils.database.player import search_player, Player

import json
import re
import os

class JX3Serendipity:
    def __init__(self):
        self.tl = []
        self.my = []
        self.jx3pet = []
        self.jx3mm = []

    def get_serendipity_level(self, serendipity_name: str) -> int:
        if serendipity_name.find("宠物奇缘") != -1:
            serendipity_level = 3
        elif serendipity_name in [serendipity[:-4] for serendipity in os.listdir(build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", "common"], end_with_slash=True))]:
            serendipity_level = 3
        elif serendipity_name in [serendipity[:-4] for serendipity in os.listdir(build_path(ASSETS, ["image", "jx3", "serendipity", "serendipity", "peerless"], end_with_slash=True))]:
            serendipity_level = 2
        else:
            serendipity_level = 1
        return serendipity_level

    async def get_tuilan_data(self, server: str, name: str):
        role: Player = await search_player(role_name=name, server_name=server)
        data = role.format_jx3api()
        if data["code"] != 200:
            return False
        global_role_id = data["data"]["globalRoleId"]
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
        data = (await Request(final_url).get()).json()
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

    async def get_jx3pet_data(self, server: str, name: str):
        final_url = f"https://www.jx3pet.com/api/serendipity?server={server}&type=不限&serendipity=不限&name={name}&limit=30"
        try:
            data = (await Request(final_url).get(timeout=2)).json()
        except:
            self.jx3pet = []
            return
        data = json.loads(re.search(r'\{.*\}', data, re.DOTALL)[0]) # type: ignore
        serendipities = []
        for serendipity in data["data"]:
            serendipities.append(
                {
                    "name": serendipity["serendipity"],
                    "level": self.get_serendipity_level(serendipity["serendipity"]),
                    "time": serendipity["time"]
                }
            )
        self.jx3pet = serendipities

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

    async def integration(self, server: str, name: str):
        await self.get_tuilan_data(server, name)
        await self.get_my_data(server, name)
        await self.get_jx3pet_data(server, name)
        await self.get_jx3mm_data(server, name)
        return sort_dict_list(merge_dict_lists(merge_dict_lists(merge_dict_lists(self.tl, self.my), self.jx3pet), self.jx3mm), "time")[::-1]