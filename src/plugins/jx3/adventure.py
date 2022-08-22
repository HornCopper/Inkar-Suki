import os
import sys
import nonebot

from pathlib import Path
from nonebot.adapters.onebot.v11 import MessageSegment

TOOLS = nonebot.get_driver().config.tools_path
sys.path.append(TOOLS)
ASSETS = TOOLS[:-5] + "assets"
from utils import get_api, get_content

async def getAdventure(adventure: str):
    info = await get_api(f"https://helper.jx3box.com/api/achievement/search?keyword={adventure}&page=1&limit=15&client=std")
    data = info["data"]["achievements"]
    if len(data) == 0:
        return {"status":404}
    achievement_list = []
    icon_list = []
    id_list = []
    simpleDesc = []
    fullDesc = []
    point = []
    map = []
    subAchievements = []
    for i in data:
        achievement_list.append(i["Name"])
        icon_list.append(i["IconID"])
        id_list.append(i["ID"])
        simpleDesc.append(i["ShortDesc"])
        fullDesc.append(i["Desc"])
        point.append(i["Point"])
        if i["SubAchievementList"] != None:
            SubAchievements = []
            for x in i["SubAchievementList"]:
                SubAchievements.append(x["Name"])
            subAchievementsMsg = "、".join(SubAchievements)
            subAchievements.append(subAchievementsMsg)
        else:
            subAchievements.append("无")
        if i["LayerName"] == None or i["SceneName"] == None:
            map.append("未知")
        else:
            map.append(i["LayerName"] + i["SceneName"])
    return {"status":200, "point": point, "achievements": achievement_list, "icon": icon_list, "id": id_list, "simpDesc": simpleDesc, "Desc": fullDesc, "subAchievements": subAchievements, "map": map}

async def getAchievementsIcon(IconID: str):
    final_path = ASSETS + "/jx3/adventure/" + IconID + ".png"
    if os.path.exists(final_path):
        return MessageSegment.image(Path(final_path).as_uri())
    else:
        image_url = f"https://icon.jx3box.com/icon/{IconID}.png"
        cache = open(ASSETS + "/jx3/adventure/" + IconID + ".png", mode = "wb")
        cache.write(await get_content(image_url))
        cache.close()
        return MessageSegment.image(Path(final_path).as_uri())
        