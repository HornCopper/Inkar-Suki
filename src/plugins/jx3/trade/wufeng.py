from pathlib import Path

from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.tools.utils.request import get_api, get_content
from src.tools.utils.time import convert_time, get_current_time
from src.tools.generate import generate, get_uuid
from src.tools.utils.path import ASSETS, CACHE, TOOLS, VIEWS
from src.tools.utils.file import read, write
from src.tools.basic.server import server_mapping
from src.tools.basic.prompts import PROMPT

from .sl import convertAttrs
from .api import toCoinImage, convert, template_msgbox, template_table

import json

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
    url = f"https://node.jx3box.com/api/node/item/search?ids=&keyword={name}&client=std&MinLevel={quality}&MaxLevel={quality}&BindType=2"
    data = []
    getdata = await get_api(url)
    for x in getdata["data"]["data"]:
        if str(x["Level"]) == str(quality):
            data.append(x)
    return data

async def getArmor(raw: str):
    attrs = convertAttrs(raw)
    if not attrs:
        return [f"您输入的装备词条有误，请确保包含以下四个要素：\n品级、属性、部位、内外功\n示例：13550内功双会头"]
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
    if server == "全服":
        result = await getAllServerWufengImg(raw)
        return result
    server = server_mapping(server, group)
    if not server:
        return [PROMPT.ServerNotExist]
    data = await getArmor(raw)
    if isinstance(data, list):
        return data
    currentStatus = 0 # 当日是否具有该物品在交易行
    try:
        itemId = data["id"]
    except:
        emg = await get_content("https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/emoji.jpg")
        return ["音卡建议您不要造无封装备了，因为没有。\n" + ms.image(emg)]
    logs = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/logs?server={server}")
    current = logs["data"]["today"]
    yesterdayFlag = False
    if current != None:
        currentStatus = 1
    else:
        if logs["data"]["yesterday"] != None:
            yesterdayFlag = True
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
    if (not currentStatus or yesterdayFlag) and detailData["data"]["prices"] == None:
        if not yesterdayFlag:
            return ["唔……该物品目前交易行没有数据。"]
        else:
            low = convert(current["LowestPrice"])
            avg = convert(current["AvgPrice"])
            high = convert(current["HighestPrice"])
            return [f"唔……该物品目前交易行没有数据，但是音卡找到了昨日的数据：\n昨日低价：{low}\n昨日均价：{avg}\n昨日高价：{high}"]
    table = []
    icon = "https://icon.jx3box.com/icon/" + str(data["IconID"]) + ".png"
    name = data["Name"]
    for each_price in detailData["data"]["prices"]:
        table_content = template_table
        toReplace_word = [["$icon", icon], ["$color", color], ["$name", name + "<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(getAttrs(data["attributes"])) + "</span>"], ["$time", convert_time(each_price["created"], "%m月%d日 %H:%M:%S")], ["$limit", str(each_price["n_count"])], ["$price", toCoinImage(convert(each_price["unit_price"]))]]
        for word in toReplace_word:
            table_content = table_content.replace(word[0], word[1])
        table.append(table_content)
        if len(table) == 12:
            break
    final_table = "\n".join(table)
    html = read(VIEWS + "/jx3/trade/trade.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"交易行 · {server} · {name}").replace("$msgbox", msgbox)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    return Path(final_path).as_uri()

async def getAllServerWufengImg(raw: str):
    servers = list(json.loads(read(TOOLS + "/basic/server.json")))
    highs = []
    lows = []
    avgs = []
    table = []
    data = await getArmor(raw)
    if isinstance(data, list):
        return data
    currentStatus = 0 # 当日是否具有该物品在交易行
    try:
        itemId = data["id"]
    except:
        emg = await get_content("https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/emoji.jpg")
        return ["音卡建议您不要造无封装备了，因为没有。\n" + ms.image(emg)]
    for server in servers:
        logs = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/logs?server={server}")
        current = logs["data"]["today"]
        yesterdayFlag = False
        if current != None:
            currentStatus = 1
        else:
            if logs["data"]["yesterday"] != None:
                yesterdayFlag = True
                currentStatus = 1
                current = logs["data"]["yesterday"]
            else:
                yesterdayFlag = 0
                currentStatus = 0
        if currentStatus:
            highs.append(current["HighestPrice"])
            avgs.append(current["AvgPrice"])
            lows.append(current["LowestPrice"])
        else:
            highs.append(0)
            avgs.append(0)
            lows.append(0)
        color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][data["Quality"]]
        detailData = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20")
        icon = "https://icon.jx3box.com/icon/" + str(data["IconID"]) + ".png"
        name = data["Name"]
        if (not currentStatus or yesterdayFlag) and detailData["data"]["prices"] == None:
            if not yesterdayFlag:
                toReplace_word = [["$icon", icon], ["$color", color], ["$name", name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(getAttrs(data["attributes"])) + "</span>"], ["$time", convert_time(get_current_time(), "%m月%d日 %H:%M:%S")], ["$limit", "N/A"], ["$price", "<span style=\"color:red\">没有数据</span>"]]
                table_content = template_table
                for word in toReplace_word:
                    table_content = table_content.replace(word[0], word[1])
                table.append(table_content)
                continue
            else:
                avg = convert(current["AvgPrice"])
                toReplace_word = [["$icon", icon], ["$color", color], ["$name", name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(getAttrs(data["attributes"])) + "</span>"], ["$time", convert_time(get_current_time(), "%m月%d日 %H:%M:%S")], ["$limit", "N/A"], ["$price", toCoinImage(avg)]]
                table_content = template_table
                for word in toReplace_word:
                    table_content = table_content.replace(word[0], word[1])
                table.append(table_content)
                continue
        each_price = detailData["data"]["prices"][0]
        table_content = template_table
        toReplace_word = [["$icon", icon], ["$color", color], ["$name", name + f"（{server}）<br><span style=\"color:rgb(0, 210, 75)\">" + " ".join(getAttrs(data["attributes"])) + "</span>"], ["$time", convert_time(each_price["created"], "%m月%d日 %H:%M:%S")], ["$limit", str(each_price["n_count"])], ["$price", toCoinImage(convert(each_price["unit_price"]))]]
        for word in toReplace_word:
            table_content = table_content.replace(word[0], word[1])
        table.append(table_content)

    fhighs = [x for x in highs if x != 0]
    favgs = [x for x in avgs if x != 0]
    flows = [x for x in lows if x != 0]
    exist_info_flag = False
    try:
        final_highest = int(sum(fhighs) / len(fhighs))
        final_avg = int(sum(favgs) / len(favgs))
        final_lowest = int(sum(flows) / len(flows))
        exist_info_flag = True
    except:
        pass
    if exist_info_flag:
        toReplace = [["$low", toCoinImage(convert(final_lowest))], ["$equal", toCoinImage(convert(final_avg))], ["$high", toCoinImage(convert(final_highest))]]
    else:
        toReplace = [["$low", "未知"], ["$equal", "未知"], ["$high", "未知"]]
    msgbox = template_msgbox.replace("当日", "全服")
    for toReplace_word in toReplace:
        msgbox = msgbox.replace(toReplace_word[0], toReplace_word[1])
    final_table = "\n".join(table)
    html = read(VIEWS + "/jx3/trade/trade.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"交易行 · 全服 · {name}").replace("$msgbox", msgbox)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    return Path(final_path).as_uri()