from src.tools.utils.request import get_api
from src.tools.basic.msg import PROMPT
from src.tools.config import Config

token = Config.jx3.api.token
bot_name = Config.bot_basic.bot_name_argument

async def item_(name: str = ""):  # 物价 <物品>
    final_url = f"{Config.jx3.api.url}/view/trade/record?robot={bot_name}&name={name}&chrome=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return ["唔……尚未收录该物品。"]
    return data["data"]["url"]