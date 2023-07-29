from typing import Literal, Tuple

from src.tools.dep import *


async def saohua_primary(subject: Literal["random", "content"]) -> Tuple[str, str]:
    full_link = f"{Config.jx3api_link}/data/saohua/{subject}"
    info = await get_api(full_link)
    data = info["data"]
    return data["text"], data["id"]


async def saohua_random():
    return await saohua_primary("random")


async def saohua_tiangou():
    return await saohua_primary("content")
