from pathlib import Path

from src.constant.jx3 import brickl, goldl, silverl, copperl

from src.tools.utils.request import get_api
from src.tools.basic.prompts import PROMPT
from src.tools.basic.server import server_mapping
from src.tools.utils.num import checknumber
from src.tools.utils.time import convert_time, get_current_time
from src.tools.generate import generate, get_uuid
from src.tools.utils.path import ASSETS, CACHE, TOOLS, VIEWS
from src.tools.utils.file import read, write

import datetime
import json

filters = ["无封","无皇","封头","封护","封裤","封项","封鞋","封囊"]
banned = ["囊","头饰","裤","护臂","腰坠","项链","鞋"]

template_msgbox = """
<div class="message-box">
    <div class="element">
        <div class="cell"><span style="color:green">当日最低价↓</span></div>
        <div class="cell">$low</div>
    </div>
    <div class="element">
        <div class="cell">当日均价</div>
        <div class="cell">$equal</div>
    </div>
    <div class="element">
        <div class="cell"><span style="color:red">当日最高价↑</span></div>
        <div class="cell">$high</div>
    </div>
</div>"""

template_table = """
<tr>
    <td class="short-column"><img src="$icon"></td>
    <td class="short-column"><span style="color:rgb$color">$name</span></td>
    <td class="short-column">$time</td>
    <td class="short-column">$limit</td>
    <td class="short-column">$price</td>
</tr>"""

async def getImg(server: str, name: str, group: str, itemList: list = []):
    if server == "全服":
        data = await getSingleImg(name)
        return data
    server_ = server_mapping(server, group)
    if not server_:
        return [PROMPT.ServerNotExist]
    for i in filters:
        if name.find(i) != -1:
            return ["唔……请勿查找无封装备！\n如果您需要查找无封装备，可以使用“交易行无封”（注意没有空格），使用方法参考：交易行无封 服务器 词条\n词条示例：13550内功双会头"]
    for i in banned:
        if name == i:
            return ["唔……请勿查找无封装备！"]
    final_list = []
    if itemList == []:
        itemData = await get_api(f"https://node.jx3box.com/api/node/item/search?ids=&keyword={name}&client=std&per=35")
        if itemData["data"]["total"] == 0:
            return ["唔……您搜索的物品尚未收录！"]
        final_list = itemData["data"]["data"]
    else:
        for i in itemList:
            itemData = await get_api(f"https://node.jx3box.com/api/node/item/search?ids=&keyword={i}&client=std&per=5")
            if itemData["data"]["total"] == 0:
                continue
            else:
                for x in itemData["data"]["data"]:
                    final_list.append(x)
    itemList_searchable = []
    for i in final_list:
        new = {}
        if i["BindType"] not in [0, 1, 2, None]:
            continue
        id = i["id"]
        itemAPIData = await get_api(f"https://next2.jx3box.com/api/item-price/{id}/logs?server={server_}&limit=20")
        if itemAPIData["data"]["logs"] == None:
            continue
        else:
            new["data"] = itemAPIData["data"]
        new["id"] = str(id)
        new["icon"] = f"https://icon.jx3box.com/icon/" + str(i["IconID"]) + ".png"
        new["name"] = i["Name"]
        new["quality"] = i["Quality"] if checknumber(i["Quality"]) else 0
        itemList_searchable.append(new)
    if len(itemList_searchable) == 1:
        currentStatus = 0 # 当日是否具有该物品在交易行
        yesterdayFlag = False
        current = itemList_searchable[0]["data"]["today"]
        if current != None:
            currentStatus = 1
        else:
            if itemList_searchable[0]["data"]["yesterday"] != None:
                yesterdayFlag = True
                currentStatus = 1
                current = itemList_searchable[0]["data"]["yesterday"]
        if currentStatus:
            toReplace = [["$low", toCoinImage(str(convert(current["LowestPrice"])))], ["$equal", toCoinImage(str(convert(current["AvgPrice"])))], ["$high", toCoinImage(str(convert(current["HighestPrice"])))]]
            msgbox = template_msgbox
            for toReplace_word in toReplace:
                msgbox = msgbox.replace(toReplace_word[0], toReplace_word[1])
        else:
            msgbox = ""
        color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][itemList_searchable[0]["quality"]]
        itemId = itemList_searchable[0]["id"]
        detailData = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server_}&limit=20")
        if (not currentStatus or yesterdayFlag) and detailData["data"]["prices"] == None:
            if not yesterdayFlag:
                return ["唔……该物品目前交易行没有数据。"]
            else:
                low = convert(current["LowestPrice"])
                avg = convert(current["AvgPrice"])
                high = convert(current["HighestPrice"])
                return [f"唔……该物品目前交易行没有数据，但是音卡找到了昨日的数据：\n昨日低价：{low}\n昨日均价：{avg}\n昨日高价：{high}"]
        table = []
        for each_price in detailData["data"]["prices"]:
            table_content = template_table
            toReplace_word = [["$icon", itemList_searchable[0]["icon"]], ["$color", color], ["$name", itemList_searchable[0]["name"]], ["$time", convert_time(each_price["created"], "%m月%d日 %H:%M:%S")], ["$limit", str(each_price["n_count"])], ["$price", toCoinImage(str(convert(each_price["unit_price"])))]]
            for word in toReplace_word:
                table_content = table_content.replace(word[0], word[1])
            table.append(table_content)
            if len(table) == 12:
                break
        final_table = "\n".join(table)
        html = read(VIEWS + "/jx3/trade/trade.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        
        final_name = itemList_searchable[0]["name"] if itemList == [] else "+".join(itemList)
        html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"交易行 · {server_} · {final_name}").replace("$msgbox", msgbox)
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, ".total", False)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()
    else:
        # 如果有多个，则分别显示近期价格，只显示最新一条
        table = []
        for each_item in itemList_searchable:
            color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][each_item["quality"]]
            itemId = each_item["id"]
            final_name = each_item["name"]
            itemData = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server_}&limit=20")
            table_content = template_table
            if itemData["data"]["prices"] == None:
                # 转用已存储的Log进行处理
                itemData = each_item["data"]["logs"][-1]
                time_that = itemData["CreatedAt"]
                timestamp = datetime.datetime.strptime(time_that, "%Y-%m-%dT%H:%M:%S+08:00")
                final_time = str(convert_time(int(timestamp.timestamp()), "%m月%d日 %H:%M:%S"))
                count = str(itemData["SampleSize"])
                table.append(table_content.replace("$icon", each_item["icon"]).replace("$color", color).replace("$name", final_name).replace("$time", final_time).replace("$limit", count).replace("$price", toCoinImage(str(convert(itemData["AvgPrice"])))))
            else:
                # 使用最新一条数据
                itemData = itemData["data"]["prices"][0]
                final_time = str(convert_time(itemData["created"], "%m月%d日 %H:%M:%S"))
                count = str(itemData["n_count"])
                table.append(table_content.replace("$icon", each_item["icon"]).replace("$color", color).replace("$name", final_name).replace("$time", final_time).replace("$limit", count).replace("$price", toCoinImage(str(convert(itemData["unit_price"])))))
        final_table = "\n".join(table)
        html = read(VIEWS + "/jx3/trade/trade.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        
        html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"交易行 · {server_} · {name}").replace("$msgbox", "")
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, ".total", False)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()

async def getSingleImg(name: str):
    table = []
    lows = []
    avgs = []
    highs = []
    for i in filters:
        if name.find(i) != -1:
            return ["唔……请勿查找无封装备！\n如果您需要查找无封装备，可以使用“交易行无封”（注意没有空格），使用方法参考：交易行无封 服务器 词条\n词条示例：13550内功双会头"]
    for i in banned:
        if name == i:
            return ["唔……请勿查找无封装备！"]
    final_list = []
    itemData = await get_api(f"https://node.jx3box.com/api/node/item/search?ids=&keyword={name}&client=std&per=35")
    if itemData["data"]["total"] == 0:
        return ["唔……您搜索的物品尚未收录！"]
    final_list = itemData["data"]["data"]
    servers = list(json.loads(read(TOOLS + "/basic/server.json")))
    for server in servers:
        itemList_searchable = []
        for i in final_list:
            new = {}
            if i["BindType"] not in [0, 1, 2, None]:
                continue
            id = i["id"]
            itemAPIData = await get_api(f"https://next2.jx3box.com/api/item-price/{id}/logs?server={server}&limit=20")
            new["data"] = itemAPIData["data"]
            new["id"] = str(id)
            new["icon"] = f"https://icon.jx3box.com/icon/" + str(i["IconID"]) + ".png"
            new["name"] = i["Name"]
            new["quality"] = i["Quality"] if checknumber(i["Quality"]) else 0
            itemList_searchable.append(new)
        if len(itemList_searchable) == 1:
            currentStatus = 0 # 当日是否具有该物品在交易行
            yesterdayFlag = False
            current = itemList_searchable[0]["data"]["today"]
            if current != None:
                currentStatus = 1
            else:
                if itemList_searchable[0]["data"]["yesterday"]  != None:
                    yesterdayFlag = True
                    currentStatus = 1
                    current = itemList_searchable[0]["data"]["yesterday"] 
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
            color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][itemList_searchable[0]["quality"]]
            itemId = itemList_searchable[0]["id"]
            icon = itemList_searchable[0]["icon"]
            detailData = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20")
            if (not currentStatus or yesterdayFlag) and detailData["data"]["prices"] == None:
                if not yesterdayFlag:
                    toReplace_word = [["$icon", icon], ["$color", color], ["$name", name + f"（{server}）"], ["$time", convert_time(get_current_time(), "%m月%d日 %H:%M:%S")], ["$limit", "N/A"], ["$price", "<span style=\"color:red\">没有数据</span>"]]
                    table_content = template_table
                    for word in toReplace_word:
                        table_content = table_content.replace(word[0], word[1])
                    table.append(table_content)
                    continue
                else:
                    avg = str(convert(current["AvgPrice"]))
                    toReplace_word = [["$icon", icon], ["$color", color], ["$name", name + f"（{server}）"], ["$time", convert_time(get_current_time(), "%m月%d日 %H:%M:%S")], ["$limit", "N/A"], ["$price", toCoinImage(avg)]]
                    table_content = template_table
                    for word in toReplace_word:
                        table_content = table_content.replace(word[0], word[1])
                    table.append(table_content)
                    continue
            each_price = detailData["data"]["prices"][0]
            table_content = template_table
            toReplace_word = [["$icon", itemList_searchable[0]["icon"]], ["$color", color], ["$name", itemList_searchable[0]["name"] + f"（{server}）"], ["$time", convert_time(each_price["created"], "%m月%d日 %H:%M:%S")], ["$limit", str(each_price["n_count"])], ["$price", toCoinImage(str(convert(each_price["unit_price"])))]]
            for word in toReplace_word:
                table_content = table_content.replace(word[0], word[1])
            table.append(table_content)
        else:
            return ["唔……您给出的物品名称似乎不够精准，全服交易行价格查询最好给出准确名称哦！"]
    fhighs = [x for x in highs if x != 0]
    favgs = [x for x in avgs if x != 0]
    flows = [x for x in lows if x != 0]
    try:
        final_highest = int(sum(fhighs) / len(fhighs))
        final_avg = int(sum(favgs) / len(favgs))
        final_lowest = int(sum(flows) / len(flows))
    except:
        return ["唔……该物品全服均没有数据！"]
    toReplace = [["$low", toCoinImage(str(convert(final_lowest)))], ["$equal", toCoinImage(str(convert(final_avg)))], ["$high", toCoinImage(str(convert(final_highest)))]]
    msgbox = template_msgbox.replace("当日", "全服")
    for toReplace_word in toReplace:
        msgbox = msgbox.replace(toReplace_word[0], toReplace_word[1])
    final_table = "\n".join(table)
    html = read(VIEWS + "/jx3/trade/trade.html")
    font = ASSETS + "/font/custom.ttf"
    saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
    
    final_name = itemList_searchable[0]["name"]
    html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"交易行 · {server} · {final_name}").replace("$msgbox", msgbox)
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()

def toCoinImage(rawString: str):
    to_replace = [["砖", f"<img src=\"{brickl}\">"], ["金", f"<img src=\"{goldl}\">"], ["银", f"<img src=\"{silverl}\">"], ["铜", f"<img src=\"{copperl}\">"]]
    for waiting in to_replace:
        rawString = rawString.replace(waiting[0], waiting[1])
    processedString = rawString
    return processedString

def convert(price: int):
    if 1 <= price <= 99:  # 铜
        return f"{price} 铜"
    elif 100 <= price <= 9999:  # 银
        silver = price // 100
        copper = price % 100
        if copper == 0:
            return f"{silver} 银"
        else:
            return f"{silver} 银 {copper} 铜"
    elif 10000 <= price <= 99999999:  # 金
        gold = price // 10000
        silver = (price % 10000) // 100
        copper = price % 100
        result = f"{gold} 金"
        if silver:
            result += f" {silver} 银"
        if copper:
            result += f" {copper} 铜"
        return result
    elif price >= 100000000:  # 砖
        brick = price // 100000000
        gold = (price % 100000000) // 10000
        silver = (price % 10000) // 100
        copper = price % 100
        result = f"{brick} 砖"
        if gold:
            result += f" {gold} 金"
        if silver:
            result += f" {silver} 银"
        if copper:
            result += f" {copper} 铜"
        return result