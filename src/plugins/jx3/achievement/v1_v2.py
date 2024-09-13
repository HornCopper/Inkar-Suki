from pathlib import Path
from typing import Optional, Union, Literal

from src.tools.basic.server import server_mapping
from src.tools.config import Config
from src.tools.basic.prompts import PROMPT
from src.tools.utils.request import get_api, post_url
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.utils.file import read, write
from src.tools.generate import generate, get_uuid
from src.tools.basic.jx3 import gen_ts, format_body, gen_xsk

from src.plugins.jx3.bind import get_player_local_data
from src.plugins.jx3.dungeon.api import get_map, zone_mapping, mode_mapping

import json

token = Config.jx3.api.token
ticket = Config.jx3.api.ticket
bot_name = Config.bot_basic.bot_name_argument
device_id = ticket.split("::")[-1]

async def achievements_(server: Optional[str] = "", name: str = "", achievement: str = "", group_id: str = ""):
    if ticket is None:
        return [PROMPT.NoTicket]
    server_ = server_mapping(server, group_id)
    if not server_:
        return [PROMPT.ServerNotExist]
    final_url = f"{Config.jx3.api.url}/view/role/achievement?server={server_}&name={achievement}&role={name}&nickname={bot_name}&ticket={ticket}&token={token}&chrome=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return [PROMPT.ServerInvalid]
    if data["data"] == {}:
        return ["唔……未找到相应成就。"]
    if data["code"] == 404:
        return ["唔……玩家名输入错误。"]
    return data["data"]["url"]

template = """
<tr>
    <td class="icon-column"><img src="$image" alt="icon" width="30"></td>
    <td class="name-column">$name</td>
    <td class="type-column">$type</td>
    <td class="description-column">$desc</td>
    <td class="qualification-column">$value</td>
    <td class="status-column"><span class="$status">$flag</span></td>
</tr>
"""


async def achi_v2(server: Optional[str] = "", name: str = "", achievement: str = "", group_id: str = ""):
    server_ = server_mapping(server, group_id)
    if not server_:
        return [PROMPT.ServerNotExist]
    personal_data_request = await get_player_local_data(role_name=name, server_name=server_)
    personal_data = personal_data_request.format_jx3api()
    if personal_data["code"] != 200:
        guid = ""
        return ["唔……玩家信息获取失败。"]
    else:
        guid = personal_data["data"]["globalRoleId"]
    param = {
        "size": 200,
        "gameRoleId": guid,
        "name": achievement,
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host": "m.pvp.xoyo.com",
        "Accept": "application/json",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "cache-control": "no-cache",
        "fromsys": "APP",
        "clientkey": "1",
        "apiversion": "3",
        "gamename": "jx3",
        "platform": "ios",
        "sign": "true",
        "token": ticket,
        "deviceid": device_id,
        "User-Agent": "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
        "x-sk": xsk
    }
    data = await post_url("https://m.pvp.xoyo.com/achievement/list/achievements", headers=headers, data=param)
    data = json.loads(data)
    data = data["data"]["data"]
    if len(data) == 0:
        return ["唔……未找到相关成就。"]
    else:
        contents = []
        for i in data:
            icon = i["icon"]
            type_ = i["detail"]
            desc = i["desc"]
            value = str(i["reward_point"])
            status = "correct" if i["isFinished"] else "incorrect"
            flag = "✔" if i["isFinished"] else "✖"
            aname = i["name"]
            new = template.replace("$image", icon).replace("$name", aname).replace("$type", type_).replace(
                "$desc", desc).replace("$value", value).replace("$status", status).replace("$flag", flag)
            contents.append(new)
        content = "\n".join(contents)
        html = read(VIEWS + "/jx3/achievement/achievement.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        
        html = html.replace("$customfont", font).replace("$tablecontent", content).replace(
            "$randomsaohua", saohua).replace("$appinfo", f" · 成就百科 · {server_} · {name} · {achievement}")
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()


async def zone_achi(
        server: Union[Optional[str], Literal[False]] = "", 
        name: str = "", 
        zone: Union[Optional[str], Literal[False]] = "", 
        mode: Union[Optional[str], Literal[False]] = ""
    ) -> Union[Optional[str], list]:
    zone_ = zone_mapping(zone)
    mode_ = mode_mapping(mode)
    if not isinstance(server, str):
        return
    if zone_ is False or mode_ is False:
        return ["唔……难度或名称输入有误。"]
    personal_data_request = await get_player_local_data(role_name=name, server_name=server)
    personal_data = personal_data_request.format_jx3api()
    if personal_data["code"] != 200:
        guid = ""
        return [f"唔……未找到该玩家，请提交角色！\n提交角色 服务器 UID"]
    else:
        guid = personal_data["data"]["globalRoleId"]
    map_id = await get_map(zone_, mode_)
    if not isinstance(map_id, str):
        return
    param = {
        "cursor": 0,
        "size": 200,
        "dungeon_map_id": int(map_id),
        "gameRoleId": guid,
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host": "m.pvp.xoyo.com",
        "Accept": "application/json",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "cache-control": "no-cache",
        "fromsys": "APP",
        "clientkey": "1",
        "apiversion": "3",
        "gamename": "jx3",
        "platform": "ios",
        "sign": "true",
        "token": ticket,
        "deviceid": device_id,
        "User-Agent": "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
        "x-sk": xsk
    }
    data = await post_url("https://m.pvp.xoyo.com/achievement/list/achievements", headers=headers, data=param)
    data = json.loads(data)
    data = data["data"]["data"]
    if len(data) == 0:
        return ["唔……未找到相关成就。"]
    else:
        contents = []
        for i in data:
            icon = i["icon"]
            type_ = i["detail"]
            desc = i["desc"]
            value = str(i["reward_point"])
            status = "correct" if i["isFinished"] else "incorrect"
            flag = "✔" if i["isFinished"] else "✖"
            aname = i["name"]
            new = template.replace("$image", icon).replace("$name", aname).replace("$type", type_).replace(
                "$desc", desc).replace("$value", value).replace("$status", status).replace("$flag", flag)
            contents.append(new)
        content = "\n".join(contents)
        html = read(VIEWS + "/jx3/achievement/achievement.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        
        html = html.replace("$customfont", font).replace("$tablecontent", content).replace(
            "$randomsaohua", saohua).replace("$appinfo", f" · 成就百科 · {server} · {name} · {mode}{zone}")
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        if not isinstance(final_path, str):
            return 
        return Path(final_path).as_uri()
