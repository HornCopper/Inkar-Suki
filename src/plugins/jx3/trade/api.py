from src.tools.dep import *

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

async def getImg(server: str, name: str, group: str):
    if token is None:
        return [PROMPT_NoToken]
    server = server_mapping(server, group)
    if not server:
        return [PROMPT_ServerNotExist]
    for i in filters:
        if name.find(i) != -1:
            return ["唔……请勿查找无封装备！"]
    for i in banned:
        if name == i:
            return ["唔……请勿查找无封装备！"]
    itemData = await get_api(f"https://node.jx3box.com/api/node/item/search?ids=&keyword={name}&client=std")
    if itemData["data"]["total"] == 0:
        return ["唔……您搜索的物品尚未收录！"]
    itemList_searchable = []
    for i in itemData["data"]["data"]:
        new = {}
        if i["BindType"] not in [0, 1, 2]:
            continue
        id = i["id"]
        itemAPIData = await get_api(f"https://next2.jx3box.com/api/item-price/{id}/logs?server={server}&limit=20")
        if itemAPIData["data"]["logs"] == None:
            continue
        else:
            new["data"] = itemAPIData["data"]
        new["id"] = id
        new["icon"] = f"https://icon.jx3box.com/icon/" + str(i["IconID"]) + ".png"
        new["name"] = i["Name"]
        new["quality"] = i["Quality"] if checknumber(i["Quality"]) else 0
        itemList_searchable.append(new)
    if len(itemList_searchable) == 1:
        currentStatus = 0 # 当日是否具有该物品在交易行
        current = itemList_searchable[0]["data"]["today"]
        if current != None:
            currentStatus = 1
        if currentStatus:
            toReplace = [["$low", toCoinImage(convert(current["LowestPrice"]))], ["$equal", toCoinImage(convert(current["AvgPrice"]))], "$high", toCoinImage(convert(current["HighestPrice"]))]
            msgbox = template_msgbox
            for toReplace_word in toReplace:
                msgbox = msgbox.replace(toReplace_word[0], toReplace_word[1])
        else:
            msgbox = ""
        color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][new["quality"]]
        itemId = itemList_searchable[0]["id"]
        detailData = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20")
        if not currentStatus and detailData["data"]["prices"] == None:
            return ["唔……该物品目前交易行没有数据。"]
        table = []
        for each_price in detailData["data"]["prices"]:
            table_content = template_table
            toReplace_word = [["$icon", itemList_searchable[0]["icon"]], ["$color", color], ["$name", itemList_searchable[0]["name"]], ["$time", convert_time(each_price["created"], "%m月%日 %H%M%S")], ["$limit", str(each_price["n_count"])], ["$price", toCoinImage(convert(each_price["unit_price"]))]]
            for word in toReplace_word:
                table_content = table_content.replace(word[0], word[1])
            table.append(table_content)
            if len(table) == 10:
                break
        final_table = "\n".join(table)
        html = read(bot_path.VIEWS + "/jx3/trade/trade.html")
        font = bot_path.ASSETS + "/font/custom.ttf"
        saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
        saohua = saohua["data"]["text"]
        final_name = itemList_searchable[0]["name"]
        html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f" · 交易行 · {server} · {final_name}")
        final_html = bot_path.CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "body", False)
        return Path(final_path).as_uri()
    else:
        # 如果有多个，则分别显示近期价格，只显示最新一条
        table = []
        for each_item in itemList_searchable:
            color = ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][new["quality"]]
            itemId = each_item["id"]
            final_name = each_item["name"]
            itemData = await get_api(f"https://next2.jx3box.com/api/item-price/{itemId}/detail?server={server}&limit=20")
            if itemData["data"]["prices"] == None:
                # 转用已存储的Log进行处理
                itemData = each_item["data"]["logs"][-1]
                time_that = itemData["CreatedAt"]
                timestamp = datetime.datetime.strptime(time_that, "%Y-%m-%dT%H:%M:%S+08:00")
                final_time = convert_time(int(timestamp.timestamp()), "%m月%日 %H%M%S")
                count = str(itemData["SampleSize"])
                table_content = template_table
                table.append(table_content.replace("$icon", each_item["icon"]).replace("$color", color).replace("$name", final_name).replace("$time", final_time).replace("$limit", count).replace("$price", toCoinImage(convert(itemData["AvgPrice"]))))
            else:
                # 使用最新一条数据
                itemData = itemData["data"]["prices"][0]
                final_time = convert_time(itemData["created"], "%m月%日 %H%M%S")
                count = itemData["n_count"]
                table.append(table_content.replace("$icon", each_item["icon"]).replace("$color", color).replace("$name", final_name).replace("$time", final_time).replace("$limit", count).replace("$price", toCoinImage(convert(itemData["unit_price"]))))
        final_table = "\n".join(table)
        html = read(bot_path.VIEWS + "/jx3/trade/trade.html")
        font = bot_path.ASSETS + "/font/custom.ttf"
        saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
        saohua = saohua["data"]["text"]
        html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"交易行 · {server} · {name}").replace("$msgbox", "")
        final_html = bot_path.CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "body", False)
        return Path(final_path).as_uri()

def toCoinImage(rawString: str):
    to_replace = [["砖", f"<img src=\"{brickl}\">"], ["金", f"<img src=\"{goldl}\">"], ["银", f"<img src=\"{goldl}\">"], ["铜", f"<img src=\"{copperl}\">"]]
    for waiting in to_replace:
        rawString = rawString.replace(waiting[0], waiting[1])
    processedString = rawString
    return processedString

def convert(price: int):
    if 1 <= price <= 99: # 铜
        return f"{price} 铜"
    elif 100 <= price <= 9999: # 银
        copper = price % 100
        silver = (price - copper) / 100
        if copper == 0:
            return str(int(silver)) + " 银" 
        else:
            return str(int(silver)) + " 银" + " " + str(int(copper)) + " 铜"
    elif 10000 <= price <= 99999999: # 金
        copper = price % 100
        silver = ((price - copper) % 10000) / 100
        gold = (price - copper - silver) / 10000
        msg = str(int(gold)) + " 金"
        if str(int(silver)) != "0":
            msg = msg + " " + str(int(silver)) + " 银"
        if str(int(copper)) != "0":
            msg = msg + " " + str(int(copper)) + " 铜"
        return msg
    elif 100000000 <= price: # 砖
        copper = price % 100
        silver: int = ((price - copper) % 10000) / 100
        gold = ((price - copper - silver*100) % 100000000) / 10000
        brick = (price - copper - silver*100 - gold*10000) / 100000000
        msg = str(int(brick)) + " 砖"
        if str(int(gold)) != "0":
            msg = msg + " " + str(int(gold)) + " 金"
        if str(int(silver)) != "0":
            msg = msg + " " + str(int(silver)) + " 银"
        if str(int(copper)) != "0":
            msg = msg + " " + str(int(copper)) + " 铜"
        return msg