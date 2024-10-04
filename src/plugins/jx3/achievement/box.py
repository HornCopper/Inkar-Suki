from typing import Literal, List
from pydantic import BaseModel

from src.utils.network import Request

class AchievementInformation(BaseModel):
    name: str
    icon: str
    id: str
    sip_desc: str
    full_desc: str
    point: str
    map: str

async def get_adventure(adventure: str) -> Literal[False] | List[AchievementInformation]:
    info = (await Request(f"https://helper.jx3box.com/api/achievement/search?keyword={adventure}&page=1&limit=15&client=std").get()).json()
    data = info["data"]["achievements"]
    if len(data) == 0:
        return False
    achievement_list: List[AchievementInformation] = []
    for each_achievement in data:
        mode = each_achievement["LayerName"] if each_achievement["LayerName"] is not None else ""
        map_name = each_achievement["SceneName"] if each_achievement["SceneName"] is not None else ""
        achievement_list.append(
            AchievementInformation(
                name = each_achievement["Name"],
                icon = "https://icon.jx3box.com/icon/" + str(each_achievement["IconID"]) + ".png",
                id = str(each_achievement["ID"]),
                sip_desc = each_achievement["ShortDesc"],
                full_desc = each_achievement["Desc"],
                point = str(each_achievement["Point"]),
                map = mode + map_name
            )
        )
    return achievement_list