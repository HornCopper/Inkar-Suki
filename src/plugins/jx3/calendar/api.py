from pathlib import Path

from src.tools.generate import get_uuid, generate
from src.tools.config import Config
from src.tools.utils.request import get_api
from src.tools.utils.file import read, write
from src.tools.utils.path import ASSETS, CACHE, VIEWS

def generate_weekday_list(start_day):
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    start_index = weekdays.index(start_day)
    weekday_list = weekdays[start_index:] + weekdays[:start_index]
    return weekday_list

template_calendar = """
<td class="day">
    <span style="font-size:40px">$day</span>
</td>
"""

template_event = """
<td>
<strong>大战：</strong>$war<br>
<strong>阵营：</strong>$camp<br>
<strong>战场：</strong>$battle<br>
<strong>驰援：</strong>$rescue<br>
<strong>门派：</strong><br>$school<br>
<strong>福缘宠物：</strong><br>$pet<br>$leader
</td>"""

world_boss = "<strong>世界首领：</strong><br>$boss"

async def getCalendar():
    api = f"{Config.jx3.api.url}/data/active/list/calendar?num=7"
    data = await get_api(api)
    data = data["data"]["data"][-8:-1]
    today = data[0]["date"]
    week_list = generate_weekday_list(data[0]["week"])
    week_list_html = []
    for i in week_list:
        week_list_html.append(f"<th>{i}</th>")
    week_list_html = "\n".join(week_list_html)
    days = []
    events = []
    for i in data:
        day = i["day"]
        days.append(template_calendar.replace("$day", day))
        leader = ""
        if "leader" in list(i):
            leader = "、".join(i["leader"])
            leader = "\n" + world_boss.replace("$boss", leader)
        war = i["war"][2:]
        camp = i["orecar"]
        battle = i["battle"]
        school = i["school"]
        rescue = i["rescue"]
        pet = "、".join(i["luck"])
        events.append(template_event.replace("$war", war).replace("$camp", camp).replace("$battle", battle).replace("$school", school).replace("$rescue", rescue).replace("$pet", pet).replace("$leader", leader))
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    appinfo = f" · 活动日历 · 自{today}起7天"
    final_days = "\n".join(days)
    final_events = "\n".join(events)
    html = read(VIEWS + "/jx3/celebrations/calendar.html")
    font = ASSETS + "/font/custom.ttf"
    html = html.replace("$customfont", font).replace("$datecontent", final_days).replace("$eventcontent", final_events).replace("$randomsaohua", saohua).replace("$appinfo", appinfo).replace("$tablehead", week_list_html)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()