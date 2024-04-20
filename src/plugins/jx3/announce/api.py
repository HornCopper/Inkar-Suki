from src.tools.basic import *

async def getAnnounce():
    final_url = f"{Config.jx3api_link}/data/news/announce?robot={bot}&token={token}"
    data = await get_api(final_url)
    return data["data"]["url"]
