from src.tools.basic import *

template_zhue = """
<tr>
    <td class="short-column">$time</td>
    <td class="short-column">$map</td>
    <td class="short-column">$relate</td>
</tr>"""

async def getZhueRecord(server: str):
    api = f"{Config.jx3.api.url}/data/server/antivice?token={token}&server={server}"
    data = await get_api(api)
    data = data["data"]
    tables = []
    for i in data:
        relateTime = getRelateTime(getCurrentTime(), i["time"])
        tables.append(template_zhue.replace("$time", convert_time(i["time"])).replace("$map", i["map_name"]).replace("$relate", relateTime))
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    appinfo_time = convert_time(getCurrentTime(), "%H:%M:%S")
    appinfo = f" · 诛恶记录 · {server} · {appinfo_time}"
    final_table = "\n".join(tables)
    html = read(VIEWS + "/jx3/celebrations/zhue.html")
    font = ASSETS + "/font/custom.ttf"
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", appinfo)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()
        
