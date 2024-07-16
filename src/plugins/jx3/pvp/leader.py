from src.tools.basic import *

bad = "<img src=\"https://jx3wbl.xoyocdn.com/img/icon-camp-bad.07567e9f.png\">"
good = "<img src=\"https://jx3wbl.xoyocdn.com/img/icon-camp-good.0db444fe.png\">"

template_leader = """
<tr>
    <td class="short-column">$server</td>
    <td class="short-column">
        $camp1
        <span style="color:$color1;font-size: large;">$status1</span><br><span style="color: rgb(87, 85, 85)">
        $time1<br>$relate1</span>
    </td>
    <td class="short-column">
        $camp2
        <span style="color:$color2;font-size: large;">$status2</span><br><span style="color: rgb(87, 85, 85)">
        $time2<br>$relate2</span>
    </td>
    <td class="short-column">
        $camp3
        <span style="color:$color3;font-size: large;">$status3</span><br><span style="color: rgb(87, 85, 85)">
        $time3<br>$relate3</span>
    </td>
</tr>
"""

def getCampIcon(camp: str):
    return good if camp == "浩气盟" else bad

def getStatusColor(status: int):
    return "red" if status == 2 else "green"

def getStatusString(status: int):
    if status == 1:
        return "可抢占"
    elif status == 2:
        return "保护期"
    elif status == 3:
        return "可拾取"

async def getLKSImage():
    url = f"{Config.jx3.api.url}/data/server/leader?token={token}"
    data = await get_api(url)
    tables = []
    for i in data["data"]:
        template = template_leader.replace("$server", i["server"])
        for x in range(0,3):
            detail = i["data"][x]
            template = template.replace("$camp" + str(x+1), getCampIcon(detail["camp_name"])).replace("$color" + str(x+1), getStatusColor(detail["status"])).replace("$status" + str(x+1), getStatusString(detail["status"])).replace("$time" + str(x+1), convert_time(detail["end_time"], "%m-%d %H:%M:%S")).replace("$relate" + str(x+1), getRelateTime(getCurrentTime(), detail["end_time"]))
        tables.append(template)
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    appinfo_time = convert_time(getCurrentTime(), "%H:%M:%S")
    appinfo = f" · 关隘首领 · {appinfo_time}"
    final_table = "\n".join(tables)
    html = read(VIEWS + "/jx3/pvp/leaders.html")
    font = ASSETS + "/font/custom.ttf"
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", appinfo)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()
        
        