from .celebrity import get_celebrity_image


async def get_pifeng_image():
    return await get_celebrity_image("披风会", 2, 3)
