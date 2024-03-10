from src.tools.basic import *

import datetime

template_chutian = """
<tr>
    <td class="short-column">$time</td>
    <td class="short-column">$site</span></td>
    <td class="short-column"><img src="$icon" style="vertical-align: middle;">$section</td>
    <td class="short-column">$desc</td>
</tr>"""

async def getChutianImg():
    processedData = await get_api("https://cms.jx3box.com/api/cms/game/celebrity?type=0")
    now_time = datetime.datetime.now()
    chour = int(now_time.strftime("%H"))
    cminute = int(now_time.strftime("%M"))
    if chour % 2 == 1 and cminute >= 30:
        t = "c11" # 单数半点 next-> c00
    elif chour % 2 == 1 and 30 > cminute >= 0:
        t = "c10" # 单数整点 next -> c11
    elif chour % 2 == 0 and cminute >= 30:
        t = "c01" # 双数半点 next -> c10
    elif chour % 2 == 0 and 30 > cminute >= 0:
        t = "c00" # 双数整点 next -> c01
    events = []
    for i in processedData["data"]:
        if i["key"] == t and i["time"] >= int(convert_time(getCurrentTime(), "%M")):
            currentSort = processedData["data"].index(i)
            events.append(processedData["data"][currentSort-2])
            events.append(processedData["data"][currentSort-1])
            events.append(processedData["data"][currentSort])
            overFlag = False
            try:
                processedData["data"][currentSort+1]
            except IndexError:
                overFlag = True
            if overFlag:
                currentSort = 0
            events.append(processedData["data"][currentSort+1])
            events.append(processedData["data"][currentSort+2])
            events.append(processedData["data"][currentSort+3])
            break
    standard = events[2]["key"] # 第二个为当前事件，标准事件
    tables = []
    for i in events:
        event = i["stage"]
        site = i["map"] + "·" + i["site"]
        icon = "https://img.jx3box.com/pve/minimap/minimap_" + i["icon"] + ".png"
        desc = i["desc"]
        hour = getHour(standard, i["key"])
        minute = str(i["time"])
        if len(minute) == 1:
            minute = "0" + minute
        final_time = str(hour) + ":" + minute
        tables.append(template_chutian.replace("$time", final_time).replace("$site", site).replace("$icon", icon).replace("$section", event).replace("$desc", desc))
    final_table = "\n".join(tables)
    html = read(VIEWS + "/jx3/celebrations/chutian.html")
    font = ASSETS + "/font/custom.ttf"
    poem = await get_api("https://v1.jinrishici.com/all.json")
    poem = poem["content"] + "——" + poem["author"] + "《" + poem["origin"] + "》"
    saohua = poem
    current_time = convert_time(getCurrentTime(), "%H:%M:%S")
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"楚天社 · {current_time}")
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()
        

def getHour(currentFlag: str, diffFlag: str):
    if currentFlag[1] == diffFlag[1]:
        result = int(convert_time(getCurrentTime(), "%H"))
    elif currentFlag == "c01" and diffFlag == "c10":
        result = int(convert_time(getCurrentTime(), "%H")) + 1
    elif currentFlag == "c11" and diffFlag == "c00":
        result = int(convert_time(getCurrentTime(), "%H")) + 1
    elif currentFlag == "c00" and diffFlag == "c11":
        result = int(convert_time(getCurrentTime(), "%H")) - 1
    elif currentFlag == "c10" and diffFlag == "c01":
        result = int(convert_time(getCurrentTime(), "%H")) - 1
    if result >= 24:
        result = result - 24
    return result