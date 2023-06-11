from src.tools.dep.api import *
from src.tools.dep.server import *

async def item_(name: str = None): # 物价 <物品>
    if token == None:
        return ["Bot尚未填写Token，请联系Bot主人~"]
    final_url = f"https://www.jx3api.com/view/trade/record?token={token}&robot={bot}&name={name}&scale=1"
    data = await get_api(final_url, proxy = proxies)
    if data["code"] == 404:
        return ["唔……尚未收录该物品。"]
    return data["data"]["url"]