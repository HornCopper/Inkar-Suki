from src.tools.basic import *

template_chutian = """
<tr>
    <td class="short-column">$time</td>
    <td class="short-column">$site</span></td>
    <td class="short-column"><img src="$icon" style="vertical-align: middle;">$section</td>
    <td class="short-column">$desc</td>
</tr>"""

async def getChutianImg():
    url = f"https://www.jx3api.com/data/active/celebrities?token={token}"
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
    poem = await get_api("https://v1.jinrishici.com/all.json")
    poem = poem["content"] + "——" + poem["author"] + "《" + poem["origin"] + "》"
    saohua = poem
    current_time = convert_time(getCurrentTime(), "%H:%M:%S")
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"楚天社 · {current_time}")
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()