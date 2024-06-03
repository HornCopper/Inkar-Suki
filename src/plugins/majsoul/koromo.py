from src.tools.basic import *

import math

koromo_api = "https://5-data.amae-koromo.com/api/v2/pl4/search_player/{player}?limit=20&tag=all"

def getRank(raw_data: dict):
    id = raw_data["level"]["id"]
    major = id % 10000
    minor = math.floor(major / 100)
    rank = "初士杰豪圣"[minor-1] if minor != 6 else "魂"
    label = rank + str(major % 100)
    return label

async def find_player(keyword: str):
    final_url = koromo_api.format(player=keyword)
    data = await get_api(final_url)
    msg = "查找到下列玩家：\n"
    if len(data) == 0:
        return "未找到任何玩家！"
    for i in data:
        msg += f"[{getRank(i)}] " + i["nickname"] + "\n"
    return msg[:-1]