from .celebrity import get_celebrity_image


async def get_qiongye_image():
    return await get_celebrity_image("穹野卫", 3, 3)
