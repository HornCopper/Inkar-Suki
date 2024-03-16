from src.tools.basic import *

template_zhue = """
<tr>
    <td class="short-column">$time</td>
    <td class="short-column">$map</td>
    <td class="short-column">$relate</td>
</tr>"""

async def getZhueRecord(server: str):
    api = f"https://www.jx3api.com/data/server/antivice?token={token}&server={server}"
    data = await get_api(api)
    data = data["data"]
    tables = []
    for i in data:
        current_time = int(datetime.now().timestamp())
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
        relateTime = f"{days}天{hours}时{minutes}分前"
        tables.append(template_zhue.replace("$time", convert_time(i["time"])).replace("$map", i["map_name"]).replace("$relate", relateTime))
    poem = await get_api("https://v1.jinrishici.com/all.json")
    poem = poem["content"] + "——" + poem["author"] + "《" + poem["origin"] + "》"
    saohua = poem
    appinfo_time = convert_time(getCurrentTime(), "%H:%M:%S")
    appinfo = f"诛恶记录 · {server} · {appinfo_time}"
    final_table = "\n".join(tables)
    html = read(VIEWS + "/jx3/item/item.html")
    font = ASSETS + "/font/custom.ttf"
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", appinfo)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()
        
