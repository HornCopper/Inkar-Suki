from src.constant.jx3 import aliases
from src.tools.config import Config
from src.tools.utils.request import get_api

async def getSnack(school: str):
    actual_name = aliases(school)
    if not actual_name:
        return "唔……没有找到该心法！"
    url = f"{Config.jx3.api.url}/data/school/toxic?name={actual_name}"
    data = await get_api(url)
    if data["code"] == 400:
        return "唔……没有找到该心法！"
    msg = f"「{actual_name}」小药：↓"
    for i in data["data"]:
        new = i["class"] + "：" + i["toxic"] + "（" + i["attribute"] + "）"
        msg = msg + "\n" + new
    return msg