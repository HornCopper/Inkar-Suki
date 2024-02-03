from src.tools.dep import *

filters = ["无封","无皇","封头","封护","封裤","封项","封鞋","封囊"]
banned = ["囊","头饰","裤","护臂","腰坠","项链","鞋"]

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
        
    else:
        # 如果有多个，则分别显示近期价格，只显示最新一条