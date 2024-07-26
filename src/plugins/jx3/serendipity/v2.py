from datetime import datetime
from pathlib import Path

from src.tools.config import Config
from src.tools.utils.request import get_api
from src.tools.basic.msg import PROMPT
from src.tools.basic.data_server import server_mapping
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.generate import get_uuid, generate
from src.tools.utils.common import convert_time
from src.tools.file import read, write

token = Config.jx3.api.token
ticket = Config.jx3.api.ticket
bot_name = Config.bot_basic.bot_name_argument

poem = "<td class=\"short-column-content\" rowspan=\"114514\"></td>" # 来点诗句

template_serendity = """
<tr>
    <td class="empty-column">
        <img src="$peerless_flag">
    </td>
    <td class="empty-column">
        <img src="$serendipity_icon" alt="$serendipity_name.png">
    </td>
    <td class="short-column">$actual_time<br>$relative_time</td>
</tr>"""

async def getImage_v2(server: str, name: str, group_id: str, type: bool):
    if token is None:
        return [PROMPT.NoToken]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT.ServerNotExist]
    data = await get_api(f"{Config.jx3.api.url}/data/luck/adventure?token={token}&server={server}&name={name}&ticket={ticket}")
    if data["code"] != 200:
        return ["唔……未找到该玩家的奇遇！"]
    # 笔记：1 → 世界奇遇；2 → 绝世奇遇；3 → 宠物奇遇
    # 注：暂时忽略宠物奇遇，不做统计
    tables = []
    current_time = int(datetime.now().timestamp())
    for i in data["data"]:
        if type and i["level"] >= 3: # 绝世+普通
            continue
        if not type and i["level"] != 3: # 宠物
            continue
        serendity_name = i["event"]
        flag = ASSETS + "/serendipity/vector/peerless.png" if i["level"] == 2 else ""
        icon = ASSETS + "/serendipity/serendipity/" + serendity_name + ".png"
        if i["time"] != 0:
            timeGet = convert_time(i["time"], format="%Y-%m-%d %H:%M:%S")
            timeGet_int = int(i["time"])
            datetime_1 = datetime.fromtimestamp(timeGet_int)
            datetime_2 = datetime.fromtimestamp(current_time)
            timedelta = datetime_2 - datetime_1
            days = int(timedelta.total_seconds() // 86400)
            hours = int((timedelta.total_seconds() - days*86400) // 3600)
            minutes = int((timedelta.total_seconds() - days*86400 - hours*3600) // 60)
            days = str(days)
            hours = str(hours)
            minutes = str(minutes)
            if len(days) == 1:
                days = "0" + days
            if len(hours) == 1:
                hours = "0" + hours
            if len(minutes) == 1:
                minutes = "0" + minutes
            relativeTime = f"{days}天{hours}时{minutes}分前"
        else:
            timeGet = "遗忘的时间"
            relativeTime = ""
        tables.append(template_serendity.replace("$peerless_flag", flag).replace("$serendipity_icon", icon).replace("$actual_time", timeGet).replace("$relative_time", relativeTime).replace("$serendipity_name", serendity_name))
    if len(tables) == 0:
        return ["唔……您似乎只有宠物奇遇哦，如果需要查看请使用V1版本的奇遇查询：\n查询v1/奇遇v1 区服 ID"]
    tables[0] = tables[0][:-5] + poem + "</tr>"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    appinfo_time = convert_time(int(datetime.now().timestamp()), "%H:%M:%S")
    appinfo = f"个人奇遇记录 · {server} · {name} · {appinfo_time}"
    final_table = "\n".join(tables)
    font = ASSETS + "/font/custom.ttf"
    html = read(VIEWS + "/jx3/serendipity/serendipity.html")
    title_image = ASSETS + "/serendipity/vector/title.png"
    poem_image = ASSETS + "/serendipity/vector/poem.png"
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", appinfo).replace("$titleimage", title_image).replace("$poem_image", poem_image)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()
