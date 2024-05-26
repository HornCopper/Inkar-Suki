from src.tools.basic import *

global_file_path = TOOLS + "/affections.json"

def getAffections():
    if not os.path.exists(global_file_path):
        write(global_file_path, "[]")
        return []
    else:
        content = read(global_file_path)
        data = json.loads(content)
        return data
    
def storgeAffections(new_data: dict):
    current = getAffections()
    current.append(new_data)
    write(global_file_path, json.dumps(current, ensure_ascii=False))
    return True
    
def checkUinStatus(uin: int):
    data = getAffections()
    for i in data:
        if uin in i["uin"]:
            return True
    return False
    
async def getSchool(name: str, server: str):
    data = await get_api(f"{Config.jx3api_link}/data/role/detailed?token={token}&server={server}&name={name}")
    if data["code"] != 200:
        return False
    else:
        return data["data"]["forceName"]

async def bind_affection(uin_1: int, name_1: str, uin_2: int, name_2: str, group_id: int, custom_time: int):
    if checkUinStatus(uin_1) or checkUinStatus(uin_2):
        return ["唔……您已经绑定情缘了，无法再绑定新的情缘！"]
    server = getGroupServer(str(group_id))
    if not server: 
        return [PROMPT_ServerNotExist]
    school_1 = await getSchool(name_1, server)
    school_2 = await getSchool(name_2, server)
    new_data = {
        "server": server,
        "uin": [uin_1, uin_2],
        "name": [name_1, name_2],
        "time": custom_time,
        "school": [school_1, school_2]
    }
    storgeAffections(new_data)
    return ["成功绑定情缘！\n可通过“查看情缘证书”生成一张情缘证书图！"]

async def delete_affection(uin: int):
    if not checkUinStatus(uin):
        return ["咱就是说，还没绑定情缘，在解除什么呢？"]
    data = getAffections()
    for i in data:
        if uin in i["uin"]:
            data.remove(i)
            write(global_file_path, json.dumps(data, ensure_ascii=False))
            return ["已解除情缘关系！"]

async def getColor(school: str):
    data = await get_api("https://inkar-suki.codethink.cn/schoolcolors")
    for i in data:
        if kftosh(i) == school:
            return data[i]
    return "#FFFFFF"

async def generateAffectionImage(uin: int):
    for i in getAffections():
        if uin in i["uin"]:
            btxbfont = ASSETS + "/font/包图小白体.ttf"
            yozaifont = ASSETS + "/font/Yozai-Medium.ttf"
            bg = ASSETS + "/image/assistance/" + str(random.randint(1, 9)) + ".jpg"
            uin_1 = i["uin"][0]
            uin_2 = i["uin"][1]
            color_1 = await getColor(i["school"][0])
            color_2 = await getColor(i["school"][1])
            img_1 = ASSETS + "/image/school/" + i["school"][0] + ".png"
            img_2 = ASSETS + "/image/school/" + i["school"][1] + ".png"
            name_1 = i["name"][0]
            name_2 = i["name"][1]
            server = i["server"]
            recognization = convert_time(i["time"], "%Y年%m月%d日")
            relate = getRelateTime(getCurrentTime(), i["time"])[:-1]
            html = read(VIEWS + "/jx3/affections/affections.html")
            html = html.replace("$btxbfont", btxbfont).replace("$yozaifont", yozaifont).replace("$bg", bg).replace("$uin1", str(uin_1)).replace("$uin2", str(uin_2)).replace("$color1", color_1).replace("$color2", color_2).replace("$img1", img_1).replace("$img2", img_2).replace("$name1", name_1).replace("$name2", name_2).replace("$server", server).replace("$time", recognization).replace("$relate", relate)
            final_html = CACHE + "/" + get_uuid() + ".html"
            write(final_html, html)
            final_path = await generate(final_html, False, ".background-container", False)
            return Path(final_path).as_uri()
    return ["咱就是说，还没绑定情缘，在生成什么呢？"]