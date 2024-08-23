from pathlib import Path

from src.tools.config import Config
from src.tools.utils.request import get_api
from src.tools.file import read, write
from src.tools.generate import generate, get_uuid
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.utils.common import getCurrentTime, convert_time

template_chutian = """
<tr>
    <td class="short-column">$time</td>
    <td class="short-column">$site</span></td>
    <td class="short-column"><img src="$icon" style="vertical-align: middle;">$section</td>
    <td class="short-column">$desc</td>
</tr>"""

async def getChutianImg():
    url = f"{Config.jx3.api.url}/data/active/celebrity"
    data = await get_api(url)
    tables = []
    for i in data["data"]:
        time = i["time"]
        icon = i["icon"] if i["icon"] != "10" else "12"
        icon = "https://img.jx3box.com/pve/minimap/minimap_" + icon + ".png"
        desc = i["desc"]
        section = i["event"]
        map = i["map_name"]
        site = i["site"]
        tables.append(template_chutian.replace("$time", time).replace("$site", map + "·" + site).replace("$icon", icon).replace("$desc", desc).replace("$section", section))
    final_table = "\n".join(tables)
    html = read(VIEWS + "/jx3/celebrations/chutian.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    current_time = convert_time(getCurrentTime(), "%H:%M:%S")
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"楚天社 · {current_time}")
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()