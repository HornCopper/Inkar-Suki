from src.tools.basic import *

def parity(num: int):
    if num % 2 == 0:
        return True
    return False

async def getYuncongImg():
    api = "https://cms.jx3box.com/api/cms/game/celebrity?type=1" # 0为楚天社 1为云从社
    data = await get_api(api)
    chour = convert_time(getCurrentTime(), "%H")
    currentFlag = "y0" if parity(int(chour)) else "y1"
    