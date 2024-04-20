from src.tools.basic import *

def generate_weekday_list(start_day):
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    start_index = weekdays.index(start_day)
    weekday_list = weekdays[start_index:] + weekdays[:start_index]
    return weekday_list

template_calendar = """
<td class="day">
    <span style="font-size:40px">$day</span><br>
    <strong>大战：</strong>$war<br>
    <strong>阵营：</strong>$camp<br>
    <strong>战场：</strong>$battle<br>
    <strong>门派：</strong>$school<br>
    <strong>驰援：</strong>$rescue
    <strong>福缘宠物：</strong><br>$pet<br>$leader
</td>
"""

world_boss = "<strong>世界首领：</strong><br>$boss"

async def getCalendar():
    api = "https://www.jx3api.com/data/active/list/calendar?num=7"
    data = await get_api(api)
    data = data["data"]["data"][-8:-1]
    today = data[0]["date"]
    week_list = generate_weekday_list(data[0]["week"])
    week_list_html = []
    for i in week_list:
        week_list_html.append(f"<th>{i}</th>")
    week_list_html = "\n".join(week_list_html)
    content = []
    for i in data:
        leader = ""
        if "leader" in list(i):
            leader = "、".join(i["leader"])
            leader = "\n" + world_boss.replace("$boss", leader)
        day = i["day"]
        war = i["war"][2:]
        camp = i["orecar"]
        battle = i["battle"]
        school = i["school"]
        rescue = i["rescue"]
        pet = "、".join(i["luck"])
        content.append(template_calendar.replace("$day", day).replace("$war", war).replace("$camp", camp).replace("$battle", battle).replace("$school", school).replace("$rescue", rescue).replace("$pet", pet))
    poem = await get_api("https://v1.jinrishici.com/all.json")
    poem = poem["content"] + "——" + poem["author"] + "《" + poem["origin"] + "》"
    saohua = poem
    appinfo = f" · 活动日历 · 自{today}起7天"
    final_table = "\n".join(content)
    html = read(VIEWS + "/jx3/celebrations/calendar.html")
    font = ASSETS + "/font/custom.ttf"
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", appinfo).replace("$tablehead", week_list_html)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()
        