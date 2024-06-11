from src.tools.basic import *

async def api_recruit(server: str, copy: str = ""):  # 团队招募 <服务器> [关键词]
    if token == None:
        return [PROMPT_NoToken]
    server = server_mapping(server)
    if not server:
        return [PROMPT_ServerNotExist]
    final_url = f"{Config.jx3api_link}/view/member/recruit?token={token}&server={server}&robot={bot}&scale=1&keyword="
    if copy != "":
        final_url = final_url + copy
    data = await get_api(final_url)
    if data["code"] == 403:
        return [PROMPT_InvalidToken]
    elif data["code"] == 400:
        return [PROMPT_ServerNotExist]
    elif data["code"] == 404:
        return ["未找到相关团队，请检查后重试~"]
    url = data["data"]["url"]

    return url

def convert_time(timestamp: int):
    time_local = time.localtime(timestamp)
    dt = time.strftime("%H:%M:%S", time_local)
    return dt

template_interserver = """
<tr>
    <td class="short-column">$sort</td>
    <td class="short-column">$flag</td>
    <td class="short-column">$name</td>
    <td class="short-column">$level</td>
    <td class="short-column">$leader</td>
    <td class="short-column">$count</td>
    <td class="short-column">$content</td>
    <td class="short-column">$time</td>
</tr>
"""

template_local = """
<tr>
    <td class="short-column">$sort</td>
    <td class="short-column">$name</td>
    <td class="short-column">$level</td>
    <td class="short-column">$leader</td>
    <td class="short-column">$count</td>
    <td class="short-column">$content</td>
    <td class="short-column">$time</td>
</tr>
"""

async def checkAd(msg: str, data: dict):
    data = data["data"]
    for x in data:
        status = []
        for num in range(len(x)):
            status.append(True)
        result = []
        for y in x:
            if msg.find(y) != -1:
                result.append(True)
            else:
                result.append(False)
        if status == result:
            return True
    return False

async def recruit_v2(server: str, actvt: str = "", local: bool = False, filter: bool = False):
    if token == None:
        return [PROMPT_NoToken]
    server = server_mapping(server)
    if not server:
        return [PROMPT_ServerNotExist]
    final_url = f"https://www.jx3api.com/data/member/recruit?token={token}&server={server}"
    if actvt != "":
        final_url = final_url + "&keyword=" + actvt
    data = await get_api(final_url)
    if data["code"] != 200:
        return ["唔……未找到相关团队，请检查后重试！"]
    adFlags = await get_api("https://inkar-suki.codethink.cn/filters")
    time_now = convert_time(data["data"]["time"])
    appinfo = f" · 招募信息 · {server} · {time_now}"
    font = ASSETS + "/font/custom.ttf"
    data = data["data"]["data"]
    contents = []
    for i in range(len(data)):
        detail = data[i]
        content = detail["content"]
        if filter:
            to_filter = await checkAd(content, adFlags)
            if to_filter:
                continue
        flag = False if not detail["roomID"] else True
        if local and flag:
            continue
        flag = "" if not detail["roomID"] else "<img src=\"https://img.jx3box.com/image/box/servers.svg\" style=\"width:20px;height:20px;\">" 
        num = str(i + 1)
        name = detail["activity"]
        level = str(detail["level"])
        leader = detail["leader"]
        count = str(detail["number"]) + "/" + str(detail["maxNumber"])
        create_time = convert_time(detail["createTime"])
        if local:
            template = template_local
            flag = ""
        else:
            template = template_interserver
        new = template.replace("$sort", num).replace("$name", name).replace("$level", level).replace("$leader", leader).replace("$count", count).replace("$content", content).replace("$time", create_time).replace("$flag", flag)
        contents.append(new)
        if len(contents) == 50:
            break
    table ="\n".join(contents)
    html = read(VIEWS + "/jx3/recruit/recruit.html")
    saohua = await get_api(f"{Config.jx3api_link}/data/saohua/random")
    saohua = saohua["data"]["text"]
    html = html.replace("$customfont", font).replace("$appinfo", appinfo).replace("$recruitcontent", table).replace("$randomsaohua", saohua)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()