from __future__ import annotations
from src.tools.basic import *


async def announce_by_jx3api():
    final_url = f"{Config.jx3api_link}/view/web/news/announce?robot={bot}&token={token}"
    data = await get_api(final_url)
    return data["data"]["url"]
