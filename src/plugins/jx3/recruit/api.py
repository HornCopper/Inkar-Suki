from pathlib import Path
from typing import Optional

from src.tools.config import Config
from src.tools.utils.request import get_api, post_url
from src.tools.basic.server import server_mapping, Zone_mapping
from src.tools.basic.prompts import PROMPT
from src.tools.utils.file import read, write
from src.tools.generate import generate, get_uuid
from src.tools.utils.path import ASSETS, CACHE, VIEWS

import time
import json

token = Config.jx3.api.token
bot_name = Config.bot_basic.bot_name_argument

async def api_recruit(server: str, copy: str = ""):  # 团队招募 <服务器> [关键词]
    if token == None:
        return [PROMPT.NoToken]
    server_ = server_mapping(server)
    if not server_:
        return [PROMPT.ServerNotExist]
    final_url = f"{Config.jx3.api.url}/view/member/recruit?token={token}&server={server_}&nickname={bot_name}&chrome=1&keyword="
    if copy != "":
        final_url = final_url + copy
    data = await get_api(final_url)
    if data["code"] == 403:
        return [PROMPT.InvalidToken]
    elif data["code"] == 400:
        return [PROMPT.ServerNotExist]
    elif data["code"] == 404:
        return ["未找到相关团队，请检查后重试~"]
    url = data["data"]["url"]

    return url

def convert_time(timestamp: int):
    time_local = time.localtime(timestamp)
    dt = time.strftime("%H:%M:%S", time_local)
    return dt

template_interserver = """
<tr>
    <td class="short-column">$sort</td>
    <td class="short-column">$flag</td>
    <td class="short-column">$name</td>
    <td class="short-column">$level</td>
    <td class="short-column">$leader</td>
    <td class="short-column">$count</td>
    <td class="short-column">$content</td>
    <td class="short-column">$time</td>
</tr>
"""

template_local = """
<tr>
    <td class="short-column">$sort</td>
    <td class="short-column">$name</td>
    <td class="short-column">$level</td>
    <td class="short-column">$leader</td>
    <td class="short-column">$count</td>
    <td class="short-column">$content</td>
    <td class="short-column">$time</td>
</tr>
"""

async def checkAd(msg: str, data: dict):
    data = data["data"]
    for x in data:
        status = []
        for num in range(len(x)):
            status.append(True)
        result = []
        for y in x:
            if msg.find(y) != -1:
                result.append(True)
            else:
                result.append(False)
        if status == result:
            return True
    return False

async def query_recruit(server: str, keyword: Optional[str] = ""):
    if Config.jx3.api.enable:
        final_url = f"{Config.jx3.api.url}/data/member/recruit?token={token}&server={server}"
        return await get_api(final_url)
    else:
        final_url = "https://www.jx3mm.com/api/uniqueapi/Apiinterface/mrecruit"
        params = {
            "S": Zone_mapping(server),
            "v": server,
            "k": keyword,
            "t": 1,
            "offset":0,
            "limit":10
        }
        data = await post_url(final_url, json=params)
        return json.loads(data)

async def recruit_v2(server: Optional[str], keyword: str = "", local: bool = False, filter: bool = False):
    if token == None:
        return [PROMPT.NoToken]
    server_ = server_mapping(server)
    if not server_:
        return [PROMPT.ServerNotExist]
    data = await query_recruit(server_, keyword)
    if data["code"] != 200:
        return ["唔……未找到相关团队，请检查后重试！"]
    adFlags = await get_api("https://inkar-suki.codethink.cn/filters")
    time_now = convert_time(data["data"]["time"])
    appinfo = f" · 招募信息 · {server_} · {time_now}"
    font = ASSETS + "/font/custom.ttf"
    data = data["data"]["data"]
    contents = []
    for i in range(len(data)):
        detail = data[i]
        content = detail["content"]
        if filter:
            to_filter = await checkAd(content, adFlags)
            if to_filter:
                continue
        flag = False if not detail["roomID"] else True
        if local and flag:
            continue
        flag = "" if not detail["roomID"] else "<img src=\"https://img.jx3box.com/image/box/servers.svg\" style=\"width:20px;height:20px;\">" 
        num = str(i + 1)
        name = detail["activity"]
        level = str(detail["level"])
        leader = detail["leader"]
        count = str(detail["number"]) + "/" + str(detail["maxNumber"])
        create_time = convert_time(detail["createTime"])
        if local:
            template = template_local
            flag = ""
        else:
            template = template_interserver
        new = template.replace("$sort", num).replace("$name", name).replace("$level", level).replace("$leader", leader).replace("$count", count).replace("$content", content).replace("$time", create_time).replace("$flag", flag)
        contents.append(new)
        if len(contents) == 50:
            break
    table ="\n".join(contents)
    html = read(VIEWS + "/jx3/recruit/recruit.html")
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    html = html.replace("$customfont", font).replace("$appinfo", appinfo).replace("$recruitcontent", table).replace("$randomsaohua", saohua)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()