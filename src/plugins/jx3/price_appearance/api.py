from src.tools.dep import *

async def item_(name: str = None): # 物价 <物品>
    if token == None:
        return [PROMPT_NoToken]
    final_url = f"{Config.jx3api_link}/view/trade/record?token={token}&robot={bot}&name={name}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 400:
        return ["唔……尚未收录该物品。"]
    return data["data"]["url"]