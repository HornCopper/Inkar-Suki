from .api import *

basic_name = "无封"

def getAttrs(data: list):
    attrs = []
    for i in data:
        if i["color"] == "green":
            label = i["label"].split("提高")
            if len(label) == 1:
                label = i["label"].split("增加")
            label = label[0].replace("等级", "").replace("值", "")
            attrs.append(label)
    return attrs

async def getData(name, quality):
    url = f"https://node.jx3box.com/api/node/item/search?ids=&keyword={name}&client=std&per=50&page="
    data = []
    for i in range(1, 114514):
        getdata = await get_api(url + str(i+1))
        if getdata["data"]["data"] == []:
            break
        for x in getdata["data"]["data"]:
            if x["BindType"] != 2:
                continue
            if str(x["Level"]) == str(quality):
                data.append(x)
    return data

async def getArmor(raw: str):
    attrs = convertAttrs(raw)
    if attrs == False:
        return [f"您输入的装备词条有误，请确保包含以下三个要素：\n品级、属性、部位\n示例：13550内功双会头"]
    parsed = attrs[0]
    place = attrs[1]
    quality = attrs[2]
    final_name = basic_name + place
    data = await getData(final_name, quality)
    if len(data) == 0:
        return [f"未查找到该{basic_name}装备！"]
    else:
        for i in data:
            if set(getAttrs(i["attributes"])) == set(parsed):
                return i
            
async def getWufengImg(raw: str, server: str, group: str):
    server = server_mapping(server, group)
    if not server:
        return [PROMPT_ServerNotExist]
    data = await getArmor(raw)
    if type(data) == type([]):
        return data
    currentStatus = 0 # 当日是否具有该物品在交易行
    try:
        itemId = data["id"]
    except:
        return [f"唔……未找到该属性的无封装备。"]
    logs = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/logs?server={server}")
    current = logs["data"]["today"]
    if current != None:
        currentStatus = 1
    else:
        if logs["data"]["yesterday"] != None:
            currentStatus = 1
            current = logs["data"]["yesterday"]
    if currentStatus:
        toReplace = [["$low", toCoinImage(convert(current["LowestPrice"]))], ["$equal", toCoinImage(convert(current["AvgPrice"]))], ["$high", toCoinImage(convert(current["HighestPrice"]))]]
        msgbox = template_msgbox
        for toReplace_word in toReplace:
            msgbox = msgbox.replace(toReplace_word[0], toReplace_word[1])
    else:
        msgbox = ""
    color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][data["Quality"]]
    detailData = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20")
    if not currentStatus and detailData["data"]["prices"] == None:
        return ["唔……该物品目前交易行没有数据。"]
    table = []
    icon = "https://icon.jx3box.com/icon/" + str(data["IconID"]) + ".png"
    name = data["Name"]
    for each_price in detailData["data"]["prices"]:
        table_content = template_table
        toReplace_word = [["$icon", icon], ["$color", color], ["$name", name], ["$time", convert_time(each_price["created"], "%m月%d日 %H:%M:%S")], ["$limit", str(each_price["n_count"])], ["$price", toCoinImage(convert(each_price["unit_price"]))]]
        for word in toReplace_word:
            table_content = table_content.replace(word[0], word[1])
        table.append(table_content)
        if len(table) == 12:
            break
    final_table = "\n".join(table)
    html = read(bot_path.VIEWS + "/jx3/trade/trade.html")
    font = bot_path.ASSETS + "/font/custom.ttf"
    saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
    saohua = saohua["data"]["text"]
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"交易行 · {server} · {name}").replace("$msgbox", msgbox)
    final_html = bot_path.CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    return Path(final_path).as_uri()

def extract_numbers(string):
    pattern = r"\d+"
    numbers = re.findall(pattern, string)
    return [int(num) for num in numbers]
 
def convertAttrs(raw: str):
    # 手搓关键词提取
    def fd(raw: str, to: str):
        if raw.find(to) != -1:
            return True
        return False

    raw = raw.replace("攻击", "")
    raw = raw.replace("攻", "")
    raw = raw.replace("品", "")

    more = []

    # 基础类型 内外功
    if fd(raw, "外"):
        basic = "外功"
    elif fd(raw, "内"):
        basic = "内功"
    else:
        return False

    more.append(basic + "攻击")

    # 基础类型 会心 破防 无双 破招（不存在纯破招无封）
    if fd(raw, "纯会"):
        if basic == "外功":
            more.append(basic + "会心")
        else:
            more.append("全会心")
    if fd(raw, "纯无"):
        more.append("无双")
    if fd(raw, "纯破"):
        more.append(basic + "破防")

    # 双会类
    if fd(raw, "双会"):
        if basic == "外功":
            more.append(basic + "会心")
            more.append(basic + "会心效果")
        else:
            more.append("全会心")
            more.append("全会心效果")

    # 双会可能出现的组合
    if fd(raw, "破") and not fd(raw, "纯破") and not fd(raw, "破招"):
        more.append(basic + "破防")
    
    if fd(raw, "招") or fd(raw, "破破"):
        more.append("破招")
    
    if fd(raw, "无") and not fd(raw, "纯无"):
        more.append("无双")
    
    # 会心
    if fd(raw, "会") and not fd(raw, "双会") and not fd(raw, "纯会"):
        if basic == "外功":
            more.append(basic + "会心")
        else:
            more.append("全会心")

    num_list = extract_numbers(raw)
    if len(num_list) != 1:
        return False
    
    # 部位
    place = ""

    quality = num_list[0]
    
    if fd(raw, "头") or fd(raw, "帽") or fd(raw, "脑壳"):
        place = "头饰"
    elif fd(raw, "手") or fd(raw, "臂"):
        place = "护臂"
    elif fd(raw, "裤") or fd(raw, "下装"):
        place = "裤"
    elif fd(raw, "鞋") or fd(raw, "jio") or fd(raw, "脚"):
        place = "鞋"
    elif fd(raw, "链") or fd(raw, "项"):
        place = "项链"
    elif fd(raw, "坠") or fd(raw, "腰"):
        if not fd(raw, "腰带"):
            place = "腰坠"
    elif fd(raw, "暗器") or fd(raw, "囊") or fd(raw, "弓弦"):
        place = "囊"
    else:
        return False

    return [more, place, quality]