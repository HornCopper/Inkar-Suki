import os
import sys
import nonebot

from pathlib import Path
from nonebot.adapters.onebot.v11 import MessageSegment

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"
from utils import get_api

async def get_buff(buffName: str):
    final_url = f"https://node.jx3box.com/buff/name/{buffName}?strict=1&per=10"
    data = await get_api(final_url)
    if data["total"] == 0:
        return "唔，没有找到你要的buff数据哦~"
    icon = []
    remarks = []
    desc = []
    name = []
    id = []
    for i in data["list"]:
        icon.append("https://icon.jx3box.com/icon/" + str(i["IconID"]) + ".png")
        remarks.append(i["Remark"])
        desc.append(i["Desc"])
        id.append(str(i["BuffID"]))
        name.append(i["Name"])
    return {"icon":icon, "remark":remarks, "desc": desc, "name":name, "id": id}