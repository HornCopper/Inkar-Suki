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

async def getImg(server: str, name: str):
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
        itemAPIData = await get_api(f"https://next2.jx3box.com/api/item-price/{id}/detail?server={server}&limit=20")
        if itemAPIData["data"]["prices"] == None:
            continue
        else:
            new["data"] = itemAPIData["data"]["prices"]
        new["icon"] = f"https://icon.jx3box.com/icon/" + i["IconID"] + ".png"
        new["name"] = i["Name"]
        new["quality"] = i["Quality"] if checknumber(i["Quality"]) else 0
        itemList_searchable.append(new)
    if len(itemList_searchable) == 1:
        currentStatus = 0 # 当日是否具有该物品在交易行
        current = await get_api(f"https://next2.jx3box.com/api/item-price/{itemList_searchable[0]}/detail?server={server}")
        if current["data"]["prices"] != None:
            currentStatus = 1
        if currentStatus:
            msgbox = template_msgbox.replace("$low", toCoinImage(convert()))
        else:
            msgbox = ""
    else:
        # 如果有多个，则分别显示近期价格，只显示最新一条

def toCoinImage(rawString: str):
    to_replace = [["砖", brickl], ["金", goldl], ["银", silverl], ["铜", copperl]]
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