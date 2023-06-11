from src.tools.dep.api import *
from src.tools.dep.server import *

async def announce_():
    final_url = f"https://www.jx3api.com/view/web/announce?robot={bot}"
    data = await get_api(final_url, proxy = proxies)
    return data["data"]["url"]