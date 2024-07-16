from src.tools.basic import *

async def item_(name: str = None):  # 物价 <物品>
    if token is None:
        return [PROMPT_NoToken]
    final_url = f"{Config.jx3.api.url}/view/trade/record?robot={bot}&name={name}&chrome=1"
    data = await get_api(final_url)
    if data["code"] == 400:
        return ["唔……尚未收录该物品。"]
    return data["data"]["url"]