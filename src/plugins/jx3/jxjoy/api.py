from src.tools.dep.api import *
from src.tools.dep.server import *

async def random__():
    full_link = "https://www.jx3api.com/data/saohua/random"
    info = await get_api(full_link, proxy = proxies)
    return info["data"]["text"]

async def tiangou_():
    full_link = "https://www.jx3api.com/data/saohua/content"
    data = await get_api(full_link, proxy = proxies)
    text = data["data"]["text"]
    return text