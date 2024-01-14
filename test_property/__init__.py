from .Jx3Player import *


async def run():
    data = await Jx3PlayerDetailInfo.from_username('破阵子', '烤冷面不加蛋')
    data = await Jx3PlayerDetailInfo.from_username('斗转星移', '云澈')
    pass
