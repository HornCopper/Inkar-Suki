from src.tools.dep import *

from .adventure import *

VIEWS = TOOLS[:-5] + "views"

try:
    from src.tools.dep.jx3.tuilan import gen_ts, gen_xsk, format_body # 收到热心网友举报，我们已对推栏的算法进行了隐藏。
except:
    pass

device_id = ticket.split("::")[1]

async def post_url(url, proxy: dict = None, headers: str = None, timeout: int = 300, data: dict = None):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects=True) as client:
        resp = await client.post(url, timeout=timeout, headers=headers, data=data)
        result = resp.text
        return result

async def achievements_(server: str = None, name: str = None, achievement: str = None, group_id: str = None):
    if token == None:
        return [PROMPT_NoToken]
    if ticket == None:
        return [PROMPT_NoTicket]
    server = server_mapping(server, group_id)
    if not server:
        return [PROMPT_ServerNotExist]
    final_url = f"{Config.jx3api_link}/view/role/achievement?server={server}&name={achievement}&role={name}&robot={bot}&ticket={ticket}&token={token}&scale=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return [PROMPT_ServerInvalid]
    if data["data"] == {}:
        return ["唔……未找到相应成就。"]
    if data["code"] == 404:
        return ["唔……玩家名输入错误。"]
    return data["data"]["url"]

template = """
<tr>
    <td class="icon-column"><img src="$image" alt="icon" width="30"></td>
    <td class="type-column">$type</td>
    <td class="description-column">$desc</td>
    <td class="qualification-column">$value</td>
    <td class="status-column"><span class="$status">$flag</span></td>
</tr>
"""

async def achi_v2(server: str = None, name: str = None, achievement: str = None, group_id: str = None):
    personal_data_request = f"{Config.jx3api_link}/data/role/detailed?token={token}&server={server}&name={name}"
    personal_data = await get_api(personal_data_request)
    if personal_data["code"] != 200:
        guid = ""
        return ["唔……玩家信息获取失败。"]
    else:
        guid = personal_data["data"]["globalRoleId"]
    param = {
        "size": 200,
        "gameRoleId": guid,
        "name": achievement,
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host": "m.pvp.xoyo.com",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "fromsys": "APP",
        "gamename": "jx3",
        "X-Sk": xsk,
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "apiversion": "3",
        "platform": "ios",
        "token": ticket,
        "deviceid": device_id,
        "Cache-Control": "no-cache",
        "clientkey": "1",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "SeasunGame/197 CFNetwork/1408.0.4 Darwin/22.5.0",
        "sign": "true"
    }
    data = await post_url("https://m.pvp.xoyo.com/achievement/list/achievements", headers=headers, data=param)
    data = json.loads(data)
    data = data["data"]["data"]
    if len(data) == 0:
        return ["唔……未找到相关成就。"]
    else:
        contents = []
        for i in data:
            icon = i["icon"]
            type_ = i["detail"]
            desc = i["desc"]
            value = str(i["reward_point"])
            status = "correct" if i["isFinished"] else "incorrect"
            flag = "✔" if i["isFinished"] else "✖"
            new = template.replace("$image", icon).replace("$type", type_).replace("$desc", desc).replace("$value", value).replace("$status", status).replace("$flag", flag)
            contents.append(new)
        content = "\n".join(contents)
        html = read(VIEWS + "/jx3/achievement/achievement.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = await get_api("https://www.jx3api.com/data/saohua/random")
        saohua = saohua["data"]["text"]
        html = html.replace("$customfont", font).replace("$tablecontent", content).replace("$randomsaohua", saohua).replace("$appinfo", f" · 成就百科 · {server} · {name} · {achievement}")
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        return Path(final_path).as_uri()

async def zone_achi(server: str = None, name: str = None, zone: str = None, mode: str = None, group_id: str = None):
    ...