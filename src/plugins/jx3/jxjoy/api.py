from src.tools.dep import *
from typing import Literal, Tuple

async def saohua_primary(subject: Literal["random", "content"]) -> Tuple[str, str]:
    full_link = f"{Config.jx3api_link}/data/saohua/{subject}"
<<<<<<< HEAD
    info = await get_api(full_link, proxy=proxies)
=======
    info = await get_api(full_link)
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0
    data = info["data"]
    return data["text"], data["id"]

async def saohua_random():
    return await saohua_primary("random")

async def saohua_tiangou():
    return await saohua_primary("content")
