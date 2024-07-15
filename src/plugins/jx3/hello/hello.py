import requests
from src.tools.basic import *
from PIL import Image
from io import BytesIO



async def world_(args: Message = CommandArg()):

    image = await get_content('https://api.southerly.top/api/60s?format=image')
    return image