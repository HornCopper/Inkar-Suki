from .celebrity import get_celebrity_image


async def get_chutian_image():
    return await get_celebrity_image("楚天社", 0, 4)
