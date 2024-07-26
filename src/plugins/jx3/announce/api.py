from src.tools.config import Config
from src.tools.utils.request import get_api

bot_name = Config.bot_basic.bot_name_argument
token = Config.jx3.api.token

async def getAnnounce():
    final_url = f"{Config.jx3.api.url}/view/web/news/announce?robot={bot_name}&token={token}"
    data = await get_api(final_url)
    return data["data"]["url"]
