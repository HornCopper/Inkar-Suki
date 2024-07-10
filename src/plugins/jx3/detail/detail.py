from src.tools.basic import *
from src.plugins.jx3.dungeon.api import post_url


async def get_tuilan_data(url: str, params: dict = None):
    if params is None:
        params = {"ts": gen_ts()}
    ticket = Config.jx3_token
    params = format_body(params)
    xsk = gen_xsk(params)
    basic_headers = {
        "Host": "m.pvp.xoyo.com",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "fromsys": "APP",
        "gamename": "jx3",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "apiversion": "3",
        "platform": "ios",
        "token": ticket,
        "deviceid": device_id,
        "Cache-Control": "no-cache",
        "clientkey": "1",
        "User-Agent": "SeasunGame/202CFNetwork/1410.0.3Darwin/22.6.0",
        "sign": "true",
        "x-sk": xsk
    }
    data = await post_url(url, headers=basic_headers, data=params)
    return json.loads(data)


async def get_guid(server: str, name: str):
    url = f"{Config.jx3api_link}/data/role/detailed?token={Config.jx3api_globaltoken}&server={server}&name={name}"
    data = await get_api(url)
    if data["code"] != 200:
        return False
    else:
        return data["data"]["globalRoleId"]


async def get_menu():  # 获取总览分类
    menu_data = await get_tuilan_data("https://m.pvp.xoyo.com/achievement/list/menu")
    logger.info(menu_data)
    for i in menu_data["data"]:
        if i["name"] == "江湖行":
            for x in i["subClass"]:
                if x["name"] == "秘境":
                    categories = []
                    for y in x["detailClass"]:
                        categories.append(y["name"])
                    return categories
            return False
    return False


async def get_total_data(guid: str, detail: str):  # 获取单项分类的数值
    param = {
        "gameRoleId": guid,
        "cursor": 0,
        "size": 10000,
        "class": "江湖行",
        "sub_class": "秘境",
        "detail": detail,
        "ts": gen_ts()
    }
    data = await get_tuilan_data("https://m.pvp.xoyo.com/achievement/list/achievements", param)
    finished = await get_value(data, guid)
    return finished


async def get_value(data: dict, guid):
    ids = []
    for i in data["data"]["data"]:
        ids.append(int(i["id"]))
        if len(i["subset"]) != 0:
            for x in i["subset"]:
                ids.append(int((x["id"])))
    param = {
        "gameRoleId": guid,
        "ts": gen_ts(),
        "ids": ids
    }
    data = await get_tuilan_data("https://m.pvp.xoyo.com/achievement/detail/achievement", param)
    total = 0
    finished = 0
    for i in data["data"]:
        if i["isFinished"]:
            finished = finished + i["reward_point"]
        total = total + i["reward_point"]
    return f"{finished}/{total}", str(int(finished/total*100)) + "%"

template = """
<tr>
    <td class="short-column">$name</td>
    <td class="short-column"><div class="progress-bar" style="margin: 0 auto;">
        <div class="progress-$relateproportion" style="width: $proportion;"></div>
        <span class="progress-text">$proportion</span>
    </div></td>
    <td class="short-column">$value</td>
</tr>
"""


def judge_relate(proportion: str):
    num = int(proportion[0:-1])
    if 0 <= num < 25:
        return "0"
    elif 25 <= num < 50:
        return "25"
    elif 50 <= num < 75:
        return "50"
    elif 75 <= num < 100:
        return "75"
    elif num == 100:
        return "100"
    else:
        raise ValueError(f"Unsupport value {num} appeared in the proportion!")


async def generate_zd_image(server: str, id: str):
    # 暂时锁死秘境总览
    # 地图总览后面再做
    detail = await get_menu()
    if not detail:
        return ["唔……获取目录失败！"]
    guid = await get_guid(server, id)
    if not guid:
        return ["唔……未查找到该玩家！"]
    content = []
    for i in detail:
        data = await get_total_data(guid, i)
        value = data[0]
        name = i
        proportion = str(data[1])
        relate = judge_relate(proportion)
        content.append(
            template
            .replace("$name", name)
            .replace("$relateproportion", relate)
            .replace("$proportion", proportion)
            .replace("$value", value)
        )
    content = "\n".join(content)
    html = read(VIEWS + "/jx3/zone_detail/zone_detail.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    appinfo_time = convert_time(getCurrentTime(), "%H:%M")
    html = html.replace("$customfont", font).replace("$tablecontent", content).replace("$randomsaohua", saohua).replace("$appinfo", f" 副本总览 · {server} · {id} · {appinfo_time}")
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()

template_each_dungeon = """
<tr>
    $header
    <td class="short-column">$mode</td>
    <td class="short-column">
        <div class="progress-bar" style="margin: 0 auto;">
            <div class="progress" style="width: $schedule;"></div>
            <span class="progress-text">$schedule</span>
        </div>
    </td>
    <td class="short-column">$num</td>
</tr>"""

template_each_dungeon_header = """
<td class="short-column" rowspan="$count">$name</td>
"""

async def get_personal_guid(server: str, id: str):
    final_url = f"{Config.jx3api_link}/data/role/detailed?token={token}&server={server}&name={id}"
    data = await get_api(final_url)
    if data["code"] != 200:
        return False
    else:
        return data["data"]["globalRoleId"]

async def get_map_all_id(map_name: str):
    final_url = "https://m.pvp.xoyo.com/achievement/list/dungeon-maps"
    data = await get_tuilan_data(final_url, {"name": map_name, "detail": True, "ts": gen_ts()})
    return data["data"]["maps"]

def get_all_map():
    return json.loads(read(PLUGINS + "/jx3/dungeon/zone.json"))

def calculate(raw_data: dict):
    done = 0
    total = 0
    for achievement in raw_data["data"]["data"]:
        if achievement["isFinished"]:
            done += achievement["reward_point"]
        total += achievement["reward_point"]
    return done, total

async def get_all_dungeon_image(server: str, id: str, group_id: str):
    server = server_mapping(server, group_id)
    if server == None:
        return [PROMPT_ServerNotExist]
    guid = await get_personal_guid(server, id)
    if not guid:
        return [PROMPT_PlayerNotExist]
    map_list = get_all_map()
    table = []
    for map in map_list:
        map_data = await get_map_all_id(map)
        mode_count = len(map_data)
        is_first = False
        for mode in map_data:
            template = template_each_dungeon
            if is_first:
                template = template.replace("$header", template_each_dungeon_header.replace("$count", str(mode_count)).replace("$name", map))
                is_first = True
            else:
                template = template.replace("$header", "")
            single_map_data = await get_tuilan_data("https://m.pvp.xoyo.com/achievement/list/achievements", {"cursor": 0, "size": 200, "dungeon_map_id": mode["id"], "gameRoleId": guid, "ts": gen_ts()})
            done, total = calculate(single_map_data)
            schedule = str(int(done / total)) + "%"
            table.append(
                template
                .replace("$mode", mode["name"])
                .replace("$schedule", schedule)
                .replace("$num", f"{done}/{total}")
            )
    html = read(VIEWS + "/jx3/achievement/global_dungeon.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    appinfo_time = convert_time(getCurrentTime(), "%H:%M")
    html = html.replace("$customfont", font).replace("$tablecontent", "\n".join(table)).replace("$randomsaohua", saohua).replace("$appinfo", f"副本分览 · {server} · {id} · {appinfo_time}")
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    return Path(final_path).as_uri()