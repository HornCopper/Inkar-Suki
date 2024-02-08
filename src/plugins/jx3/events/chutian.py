from src.tools.dep import *

import datetime

template_chutian = """
<tr>
    <td class="short-column">$time</td>
    <td class="short-column">$map·$place</span></td>
    <td class="short-column"><img src="$icon" style="vertical-align: middle;">$section</td>
    <td class="short-column">$desc</td>
</tr>"""

async def processData():
    api = "https://cms.jx3box.com/api/cms/game/celebrity?type=0"
    data = await get_api(api)
    processed = {
        "c00": [],
        "c01": [],
        "c10": [],
        "c11": []
    }
    for i in data["data"]:
        processed[i["key"]].append(i)
    return processed

async def getChutianImg():
    processedData = await processData()
    now_time = datetime.datetime.now()
    hour = int(now_time.strftime("%H"))
    minute = int(now_time.strftime("%M"))
    if hour % 2 == 1 and minute >= 30:
        t = "c11" # 单数半点
    elif hour % 2 == 1 and 30 > minute >= 0:
        t = "c10" # 单数整点
    elif hour % 2 == 0 and minute >= 30:
        t = "c01" # 双数半点
    elif hour % 2 == 0 and 30 > minute >= 0:
        t = "c00" # 双数整点
    # 时间轴：双数整点 -> 双数半点 -> 单数整点 -> 单数半点
    # 代码轴：c00 -> c01 -> c10 -> c11
    typeList = ["c00", "c01", "c10", "c11"]
    for i in range(len(processedData[t])):
        x = processedData[t][i]
        if x["key"] == t and x["time"] <= minute:
            final_data = []
            try:
                if i-1 == -1:
                    raise IndexError("Cannot accept the value below 0.")
                final_data.append(processedData[t][i-1])
            except IndexError:
                previous = typeList.index(t) - 1
                if previous == -1:
                    previous = 3
                final_data.append(processedData[typeList[previous]][:1])
            final_data.append(x)
            for num in range(3):
                try:
                    final_data.append(processedData[t][i+1+num])
                except IndexError:
                    next = typeList.index(t) + 1
                    if next == 4:
                        next = 0
                    final_data.append(processedData[typeList[next]][num-1])
    table = []
    for i in final_data:
        icon = "https://img.jx3box.com/pve/minimap/minimap_" + i["icon"] + ".png"
        hour = processHour(t, i["key"], int(hour))
        minute = str(i["time"])
        if len(minute) == 1:
            minute = "0" + minute
        at_map = i["map"]
        site = i["site"]
        section = i["stage"]
        desc = i["desc"]
        table.append(template_chutian.replace("$time", str(hour) + ":" + str(minute)).replace("$map", at_map).replace("$place", site).replace("$icon", icon).replace("$section", section).replace("$desc", desc))
    final_table = "\n".join(table)
    html = read(bot_path.VIEWS + "/jx3/celebrations/chutian.html")
    font = bot_path.ASSETS + "/font/custom.ttf"
    saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
    saohua = saohua["data"]["text"]
    current_time = datetime.datetime.now().strftime("%H:%M")
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"楚天社 · {current_time}")
    final_html = bot_path.CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()

def processHour(current: str, goal: str, hour: int):
    if current == goal:
        return hour
    # c00双整 c01双半 c10单整 c11单半
    elif current == "c00" and goal == "c01":
        return hour
    elif current == "c01" and goal == "c10":
        hour = hour + 1
        if hour == 24:
            return 0
    elif current == "c10" and goal == "c11":
        return hour
    elif current == "c11" and goal == "c00":
        hour = hour + 1
        if hour == 24:
            return 0
    elif current == "c11" and goal == "c10":
        return hour
    elif current == "c10" and goal == "c01":
        hour = hour - 1
        if hour == -1:
            return 23
    elif current == "c01" and goal == "c00":
        return hour
    elif current == "c00" and goal == "c11":
        hour = hour - 1
        if hour == 23:
            return 0
    else:
        raise ValueError("The current key and the goal key must be adjacent!")