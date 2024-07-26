from nonebot.adapters.onebot.v11 import MessageSegment as ms
from pathlib import Path

from src.tools.utils.request import get_api, get_content
from src.tools.utils.path import ASSETS

import os

async def getAdventure(adventure: str):
    # 数据来源@JX3BOX
    info = await get_api(f"https://helper.jx3box.com/api/achievement/search?keyword={adventure}&page=1&limit=15&client=std")
    data = info["data"]["achievements"]
    if len(data) == 0:
        return {"status": 404}
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
        if i["SubAchievementList"] is not None:
            SubAchievements = []
            for x in i["SubAchievementList"]:
                SubAchievements.append(x["Name"])
            subAchievementsMsg = "、".join(SubAchievements)
            subAchievements.append(subAchievementsMsg)
        else:
            subAchievements.append("无")
        if i["LayerName"] is None or i["SceneName"] is None:
            map.append("未知")
        else:
            map.append(i["LayerName"] + i["SceneName"])
    return {"status": 200, "point": point, "achievements": achievement_list, "icon": icon_list, "id": id_list, "simpDesc": simpleDesc, "Desc": fullDesc, "subAchievements": subAchievements, "map": map}


async def getAchievementsIcon(IconID: str):
    final_path = ASSETS + "/jx3/adventure/" + IconID + ".png"
    if os.path.exists(final_path):
        return ms.image(Path(final_path).as_uri())
    else:
        image_url = f"https://icon.jx3box.com/icon/{IconID}.png"
        with open(ASSETS + "/jx3/adventure/" + IconID + ".png", mode="wb") as cache:
            cache.write(await get_content(image_url))
        return ms.image(Path(final_path).as_uri())
