from src.tools.basic import *

from .chutian import template_chutian

def parity(num: int):
    if num % 2 == 0:
        return True
    return False

async def getYuncongImg():
    api = "https://cms.jx3box.com/api/cms/game/celebrity?type=1" # 0为楚天社 1为云从社
    data = await get_api(api)
    chour = convert_time(getCurrentTime(), "%H")
    cminute = convert_time(getCurrentTime(), "%M")
    currentFlag = "y0" if parity(int(chour)) else "y1"
    data = data["data"]
    common = data[:-3]
    events = []
    diff = []
    same = []
    for i in common:
        if i["key"] == currentFlag:
            same.append(i)
        else:
            diff.append(i)
    for i in common:
        if i["key"] == currentFlag:
            if int(cminute) <= i["time"]:
                current = common.index(i)
                if common[current-1]["key"] != common[current]["key"]:
                    common[current-1]["hour"] = str(int(chour) - 1)
                else:
                    common[current-1]["hour"] = chour
                events.append(common[current-1])
                events.append(common[current])
                for x in range(4)[1:]:
                    add = current + x
                    if add + 1 > len(common):
                        add = add - len(common) -1
                    if common[add]["key"] != common[current]["key"]:
                        common[add]["key"] = str(int(chour) + 1)
                    events.append(common[add])
            else:
                continue
        current = len(same) - 1
        common[current - 1]["hour"] = chour
        events.append(common[current - 1])
        common[current]["hour"] = chour
        events.append(common[current])
        common[0]["hour"] = str(int(chour) + 1)
        events.append(diff[0])
        common[1]["hour"] = str(int(chour) + 1)
        events.append(diff[1])
        common[2]["hour"] = str(int(chour) + 1)
        events.append(diff[2])
        common[3]["hour"] = str(int(chour) + 1)
        events.append(diff[3])
        break
        
    tables = []
    for i in events:
        hour = str(i["hour"])
        minute = str(i["time"])
        if len(hour) == 1:
            hour = "0" + hour
        if len(minute) == 1:
            minute = "0" + minute
        time = f"{hour}:{minute}"
        desc = i["desc"]
        section = i["stage"]
        map = i["map"]
        site = i["site"]
        icon = "https://img.jx3box.com/pve/minimap/minimap_" + i["icon"] + ".png"
        tables.append(template_chutian.replace("$time", time).replace("$site", map + "·" + site).replace("$icon", icon).replace("$desc", desc).replace("$section", section))
    final_table = "\n".join(tables)
    html = read(VIEWS + "/jx3/celebrations/chutian.html")
    font = ASSETS + "/font/custom.ttf"
    poem = await get_api("https://v1.jinrishici.com/all.json")
    poem = poem["content"] + "——" + poem["author"] + "《" + poem["origin"] + "》"
    saohua = poem
    current_time = convert_time(getCurrentTime(), "%H:%M:%S")
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"云从社 · {current_time}")
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()