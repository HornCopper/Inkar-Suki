from jinja2 import Template

from src.const.jx3.server import Server
from src.const.prompts import PROMPT
from src.const.path import ASSETS, build_path
from src.utils.network import Request
from src.utils.time import Time
from src.utils.database.player import search_player
from src.utils.generate import generate
from src.templates import SimpleHTML, get_saohua

from ._template import msg_box, template_arena_record

class Indicator:
    def __init__(self, server: str = "", name: str = ""):
        self.server = server
        self.name = name
        self._role_id = None
        self._person_id = None
        self._person_data = None

    async def get_role_id(self) -> bool | str:
        if self._role_id is None:
            role_info = await search_player(role_name=self.name, server_name=self.server)
            role_id = role_info.roleId
            if role_id == "":
                return False
            self._role_id = role_id
        return self._role_id

    async def get_person_info(self, roleId: str) -> dict | None:
        if self._person_data is None:
            params = {
                "role_id": roleId,
                "zone": Server(self.server).zone,
                "server": self.server,
            }
            self._person_data = (await Request("https://m.pvp.xoyo.com/role/indicator", params=params).post(tuilan=True)).json()
        return self._person_data

    async def get_person_id(self) -> bool | str | None:
        if self._person_id is None:
            role_id = await self.get_role_id()
            if not isinstance(role_id, str):
                return
            person_data = await self.get_person_info(role_id)
            if not person_data or "data" not in person_data:
                return False
            self._person_id = person_data["data"]["person_info"]["person_id"]
        return self._person_id

    async def get_arena_info(self, mode: str = "22") -> dict | None:
        person_id = await self.get_person_id()
        if not person_id:
            return None
        if not isinstance(person_id, str):
            return
        data = await self.get_person_info(person_id)
        if data and "data" in data:
            match_key = mode[0] + "c"
            for pvp_data in data["data"].get("indicator", []):
                if pvp_data["type"] == match_key:
                    return pvp_data.get("performance")
        return None

    async def get_person_arena_record(self) -> dict:
        person_id = await self.get_person_id()
        params = {
            "person_id": person_id,
            "size": 10,
            "cursor": 0
        }
        arena_record_data = (await Request("https://m.pvp.xoyo.com/mine/match/person-history", params=params).post(tuilan=True)).json()
        return arena_record_data

async def get_arena_record(server: str = "", name: str = ""):
    indicator = Indicator(server, name)
    role_id = await indicator.get_role_id()
    if not role_id or not isinstance(role_id, str):
        return PROMPT.PlayerNotExist
    await indicator.get_person_info(role_id)
    msgbox = []
    for mode in ["22", "33", "55"]:
        data = await indicator.get_arena_info(mode)
        if data is None:
            continue
        input_params = {
            "rank": f"{mode[0]}v{mode[-1]}<br>" + str(data["grade"]) + "段",
            "count": str(data["total_count"]),
            "win": str(data["win_count"]),
            "percent": str(round(data["win_count"] / data["total_count"] * 100, 2)) + "%",
            "score": str(data["mmr"]),
            "best": str(data["mvp_count"]),
            "rank_": data["ranking"]
        }
        msgbox.append(Template(msg_box).render(**input_params))
    record = await indicator.get_person_arena_record()
    tables = []
    for i in record["data"]:
        delta = i["mmr"]
        if delta > 0:
            delta = "+" + str(delta)
        else:
            delta = str(delta)
        input_params = {
            "kungfu": "https://dl.pvp.xoyo.com/static/tuilan-app/images/jx3/forces/kungfu/" + i["kungfu"] + ".png",
            "rank": str(i["avg_grade"]),
            "mode": str(i["pvp_type"]) + "V" + str(i["pvp_type"]),
            "time": Time(i["start_time"]).format("%m月%d日 %H:%M:%S"),
            "relate": Time().relate(i["end_time"]),
            "length": "共" + str(i["end_time"] - i["start_time"]) + "秒",
            "score": str(i["total_mmr"]),
            "delta": delta,
            "color": "green" if i["mmr"] > 0 else "red",
            "status": "win" if i["won"] else "lose",
            "result": "胜利" if i["won"] else "失败"
        }
        input_params["mvp_color"] = "gold" if i["mvp"] else "lightgrey"
        tables.append(Template(template_arena_record).render(**input_params))
    final_input = {
        "custom_font": build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
        "msgbox": "\n".join(msgbox),
        "table": "\n".join(tables),
        "server": server,
        "name": name,
        "saohua": get_saohua()
    }
    html = str(
        SimpleHTML(
            "jx3",
            "arena_record",
            **final_input
        )
    )
    image = await generate(html, ".container", segment=True)
    return image