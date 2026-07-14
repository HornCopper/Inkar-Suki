from .celebrity import get_celebrity_image


async def get_yuncong_image():
    return await get_celebrity_image("云从社", 1, 4)
