from typing import Literal

from src.tools.utils.request import get_api
from src.tools.config import Config

token = Config.jx3.api.token

async def saohua_primary(subject: Literal["random", "content"]):
    full_link = f"{Config.jx3.api.url}/data/saohua/{subject}?token={token}"
    info = await get_api(full_link)
    data = info and info.get("data")
    if data is None:
        return None, None
    text, id = data.get("text"), data.get("id")
    return text, id
