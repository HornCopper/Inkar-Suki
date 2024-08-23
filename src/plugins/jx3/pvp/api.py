from typing import Union, Literal, Optional
from pathlib import Path
from jinja2 import Template

from src.tools.config import Config
from src.tools.basic.msg import PROMPT
from src.tools.file import read, write
from src.tools.generate import generate, get_uuid
from src.tools.basic.data_server import server_mapping, Zone_mapping
from src.tools.utils.request import post_url
from src.tools.utils.common import convert_time, getRelateTime, getCurrentTime
from src.tools.basic.jx3 import gen_ts, gen_xsk, format_body
from src.tools.utils.path import ASSETS, CACHE, VIEWS

from src.plugins.jx3.bind.role import get_player_local_data, Player

import json

token = Config.jx3.api.token
ticket = Config.jx3.api.ticket
bot_name = Config.bot_basic.bot_name_argument
device_id = ticket.split("::")[-1]


async def get_tuilan_data(url: str, params: Union[dict, None] = None) -> dict:
    if params is None:
        params = {"ts": gen_ts()}
    params_ = format_body(params)
    xsk = gen_xsk(params_)
    basic_headers = {
        "Host": "m.pvp.xoyo.com",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "fromsys": "APP",
        "gamename": "jx3",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "apiversion": "3",
        "platform": "ios",
        "token": ticket,
        "deviceid": device_id,
        "Cache-Control": "no-cache",
        "clientkey": "1",
        "User-Agent": "SeasunGame/202CFNetwork/1410.0.3Darwin/22.6.0",
        "sign": "true",
        "x-sk": xsk
    }
    data = await post_url(url, headers=basic_headers, data=params_)
    return json.loads(data)

class Indicator:
    def __init__(self, server: str = "", name: str = ""):
        self.server = server
        self.name = name
        self._role_id = None
        self._person_id = None
        self._person_data = None

    async def get_role_id(self) -> Union[bool, str]:
        if self._role_id is None:
            role: Player = await get_player_local_data(role_name=self.name, server_name=self.server)
            role_data = role.format_jx3api()
            if role_data["code"] != 200:
                return False
            self._role_id = role_data["data"]["roleId"]
        return self._role_id

    async def get_person_info(self, roleId: str) -> Optional[dict]:
        if self._person_data is None:
            params = {
                "role_id": roleId,
                "zone": Zone_mapping(self.server),
                "server": self.server,
                "ts": gen_ts()
            }
            self._person_data = await get_tuilan_data("https://m.pvp.xoyo.com/role/indicator", params=params)
        return self._person_data

    async def get_person_id(self) -> Optional[Union[bool, str]]:
        if self._person_id is None:
            role_id = await self.get_role_id()
            if not isinstance(role_id, str):
                return
            person_data = await self.get_person_info(role_id)
            if not person_data or "data" not in person_data:
                return False
            self._person_id = person_data["data"]["person_info"]["person_id"]
        return self._person_id

    async def get_arena_info(self, mode: Literal["22", "33", "55"] = "22") -> Optional[list]:
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
                    print(pvp_data.get("performance"))
                    return pvp_data.get("performance")
        return None

    async def get_person_arena_record(self) -> dict:
        person_id = await self.get_person_id()
        params = {
            "person_id": person_id,
            "size": 10,
            "cursor": 0,
            "ts": gen_ts()
        }
        arena_record_data = await get_tuilan_data("https://m.pvp.xoyo.com/mine/match/person-history", params=params)
        return arena_record_data


msg_box = """
<div class="message-box">
    <div class="element">
        <div class="cell"><span>段位</span></div>
        <div class="cell">{{ rank }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>总场次</span></div>
        <div class="cell">{{ count }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>胜利</span></div>
        <div class="cell">{{ win }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>胜率</span></div>
        <div class="cell">{{ percent }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>评分</span></div>
        <div class="cell">{{ score }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>最佳</span></div>
        <div class="cell">{{ best }}</div>
    </div>
    <div class="element">
        <div class="cell"><span>排名（周）</span></div>
        <div class="cell">{{ rank_ }}</div>
    </div>
</div>"""

template_arena_record = """
<tr>
    <td class="short-column"><img src="{{ kungfu }}" width="30px" height="30px"></td>
    <td class="short-column">{{ rank }}段局<br>{{ mode }}</td>
    <td class="short-column">{{ time }}<br>{{ relate }} {{ length }}</td>
    <td class="short-column">{{ score }}<span style="color:{{ color }}">（{{ delta }}）</span></td>
    <td class="short-column"><span style="color: {{ color }}">{{ status }}</span></td>
</tr>"""

async def arena_record(server: Optional[str] = "", name: str = "", group_id: str = "") -> Optional[Union[list, str]]:
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    indicator = Indicator(server, name)
    role_id = await indicator.get_role_id()
    if not role_id or not isinstance(role_id, str):
        return [PROMPT.PlayerNotExist]
    await indicator.get_person_info(role_id)
    msgbox = []
    for mode in ["22", "33", "55"]:
        data = await indicator.get_arena_info(mode) # type: ignore
        if data == None:
            continue
        input_params = {
            "rank": f"{mode[0]}v{mode[-1]} · " + str(data["grade"]) + "段", # type: ignore
            "count": str(data["total_count"]), # type: ignore
            "win": str(data["win_count"]), # type: ignore
            "percent": str(round(data["win_count"] / data["total_count"] * 100, 2)) + "%", # type: ignore
            "score": str(data["mmr"]), # type: ignore
            "best": str(data["mvp_count"]), # type: ignore
            "rank_": data["ranking"] # type: ignore
        }
        msgbox.append(Template(msg_box).render(**input_params))
    record = await indicator.get_person_arena_record()
    tables = []
    for i in record["data"]:
        input_params = {
            "kungfu": "https://dl.pvp.xoyo.com/static/tuilan-app/images/jx3/forces/kungfu/" + i["kungfu"] + ".png",
            "rank": str(i["avg_grade"]),
            "mode": str(i["pvp_type"]) + "v" + str(i["pvp_type"]),
            "time": convert_time(i["start_time"], "%m月%d日 %H:%M:%S"),
            "relate": getRelateTime(getCurrentTime(), i["end_time"]),
            "length": "共" + str(i["end_time"] - i["start_time"]) + "秒",
            "score": str(i["total_mmr"]),
            "delta": str(i["mmr"]),
            "color": "green" if i["mmr"] > 0 else "red",
            "status": "WIN" if i["won"] else "LOST"
        }
        if i["mvp"]:
            input_params["status"] = input_params["status"] + "(MVP)"
        tables.append(Template(template_arena_record).render(**input_params))
    final_input = {
        "custom_font": ASSETS + "/font/custom.ttf",
        "msgbox": "\n".join(msgbox),
        "table": "\n".join(tables),
        "app": "名剑战绩",
        "server": server,
        "name": name,
        "saohua": "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    }
    html = Template(read(VIEWS + "/jx3/pvp/record.html")).render(**final_input)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()
        
    

# async def arena_record(server: str = "", name: str = "", mode: str = "", group_id: str = ""):
#     if ticket == None:
#         return [PROMPT.NoTicket]
#     server = server_mapping(server, group_id)
#     if not server:
#         return [PROMPT.ServerNotExist]
#     final_url = f"{Config.jx3.api.url}/view/match/recent?token={token}&name={name}&server={server}&nickname={bot_name}&ticket={ticket}&mode={mode}&chrome=1"
#     data = await get_api(final_url)
#     if data["code"] == 400:
#         return [PROMPT.ServerInvalid]
#     if data["code"] == 404:
#         return [f"唔……未找到该玩家，请提交角色！\n提交角色 服务器 UID"]
#     return data["data"]["url"]

# async def arena_rank(mode: str = "33"):
#     final_url = f"{Config.jx3.api.url}/view/match/awesome?token={token}&nickname={bot_name}&ticket={ticket}&mode={mode}&chrome=1"
#     data = await get_api(final_url)
#     if data["code"] == 400:
#         return ["唔……名剑模式输入错误。"]
#     return data["data"]["url"]

# async def arena_stastic(mode: str = "33"):
#     final_url = f"{Config.jx3.api.url}/view/match/schools?token={token}&nickname={bot_name}&ticket={ticket}&mode={mode}&chrome=1"
#     data = await get_api(final_url)
#     if data["code"] == 400:
#         return ["唔……名剑模式输入错误。"]
#     return data["data"]["url"]