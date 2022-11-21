import nonebot
import sys

from pathlib import Path

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"

from utils import get_api

async def search_item_info(item_name: str):
    final_url = f"https://helper.jx3box.com/api/item/search?keyword={item_name}"
    box_data = await get_api(final_url)
    if len(box_data["data"]["data"]) == 0:
        return []
    space = []
    for i in box_data["data"]["data"]:
        new = [i["id"],i["Name"]]
        space.append(new)
    return space

async def getItemPriceById(id: str, server: str):
    final_url = f"https://next2.jx3box.com/api/item-price/{id}/logs"
    data = await get_api(final_url)
    if data["code"] == 0:
        return {"msg":"唔……交易行没有此物品哦~"}
    logs = data["data"]["logs"]
    logs.reverse()
    for i in logs:
        if i["Server"] == server:
            LowestPrice = convert(i["LowestPrice"])
            AvgPrice = convert(i["AvgPrice"])
            HighestPrice = convert(i["HighestPrice"])
            return [LowestPrice, AvgPrice, HighestPrice]

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
        silver = ((price - copper) % 10000) / 100
        gold = ((price - copper - silver) % 1000000) / 10000
        brick = (price - copper - silver - gold) / 100000000
        msg = str(int(brick)) + " 砖"
        if str(int(gold)) != "0":
            msg = msg + " " + str(int(gold)) + " 金"
        if str(int(silver)) != "0":
            msg = msg + " " + str(int(silver)) + " 银"
        if str(int(copper)) != "0":
            msg = msg + " " + str(int(copper)) + " 铜"
        return msg