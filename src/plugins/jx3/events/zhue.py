from pathlib import Path

from src.tools.config import Config
from src.tools.utils.request import get_api
from src.tools.utils.file import read, write
from src.tools.generate import generate, get_uuid
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.utils.time import get_current_time, convert_time, get_relate_time
from src.tools.basic.server import Zone_mapping

import json
import time

token = Config.jx3.api.token

template_zhue = """
<tr>
    <td class="short-column">$time</td>
    <td class="short-column">$map</td>
    <td class="short-column">$relate</td>
</tr>"""

async def getZhueRecord(server: str):
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Microsoft Edge\";v=\"114\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Referer": "https://www.jx3mm.com/jx3fun/jevent/index.html"
    }
    filter = {
        "Zone": Zone_mapping(server),
        "Srv": server
    }
    base_params = {
        "sort": "Tm",
        "order": "desc",
        "limit": 30,
        "offset": 0,
        "_": int(time.time()) * 1000,
        "filter": json.dumps(filter, ensure_ascii=False),
        "op": "{\"Zone\":\"LIKE\",\"Srv\":\"LIKE\"}"
    }
    api = "https://www.jx3mm.com/jx3fun/jevent"
    data = await get_api(api, headers=headers, params=base_params)
    data = data["rows"]
    tables = []
    for i in data:
        relateTime = get_relate_time(get_current_time(), i["Tm"])
        tables.append(template_zhue.replace("$time", str(convert_time(i["Tm"]))).replace("$map", i["Content"]).replace("$relate", relateTime))
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    appinfo_time = convert_time(get_current_time(), "%H:%M:%S")
    appinfo = f" · 诛恶记录 · {server} · {appinfo_time}"
    final_table = "\n".join(tables)
    html = read(VIEWS + "/jx3/celebrations/zhue.html")
    font = ASSETS + "/font/custom.ttf"
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", appinfo)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()
        
