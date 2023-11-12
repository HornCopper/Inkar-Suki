from src.tools.dep import *

async def announce_():
    final_url = f"{Config.jx3api_link}/view/web/news/announce?robot={bot}&token={token}"
    data = await get_api(final_url, proxy=proxies)
    return data["data"]["url"]
