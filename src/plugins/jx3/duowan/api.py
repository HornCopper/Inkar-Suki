from src.tools.basic import *

from ..private import good, bad

template_tongzhan = """
<tr>
    <td class="short-column"><img src="$channel_icon"></td>
    <td class="short-column">$channel_name</td>
    <td class="short-column">
    <strong>频道：</strong>$channel_num
    <br>
    <strong>在线：</strong>$channel_online
    <br>
    <strong>阵营：</strong>
    $camp_icon$camp_name</td>
</tr>"""

async def getTongzhan(server: str):
    api = f"{Config.jx3.api.url}/data/duowan/statistical?token={token}&server={server}"
    data = await get_api(api)
    data = data["data"]
    tables = []
    for i in data[0]["data"]:
        channel_icon = i["logoUrl"]
        channel_name = i["snick"]
        channel_num = i["asid"]
        channel_online = i["users"]
        camp_name = i["campName"]
        camp_icon = good if camp_name == "浩气盟" else bad
        tables.append(template_tongzhan.replace("$channel_icon", channel_icon).replace("$channel_name", channel_name).replace("$channel_num", str(channel_num)).replace("$channel_online", str(channel_online)).replace("$camp_icon", camp_icon).replace("$camp_name", camp_name))
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    appinfo_time = convert_time(getCurrentTime(), "%H:%M:%S")
    appinfo = f" · 统战YY · {server} · {appinfo_time}"
    final_table = "\n".join(tables)
    html = read(VIEWS + "/jx3/pvp/tongzhan.html")
    font = ASSETS + "/font/custom.ttf"
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", appinfo)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()