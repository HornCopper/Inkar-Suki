from typing import Literal, Tuple

from src.tools.basic import *


async def saohua_primary(subject: Literal["random", "content"]) -> Tuple[str, str]:
    full_link = f"{Config.jx3api_link}/data/saohua/{subject}?token={token}"
    info = await get_api(full_link)
    data = info and info.get("data")
    if data is None:
        return None, None
    text, id = data.get("text"), data.get("id")
    return text, id


async def saohua_random():
    await saohua_primary("random")


async def saohua_tiangou():
    await saohua_primary("content")
