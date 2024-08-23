from src.tools.utils.request import get_api
from src.tools.config import Config

async def news_(token: str = ""):
    full_link = f"{Config.jx3.api.url}/data/news/allnews?limit=5"
    info = await get_api(full_link)

    def dtut(date, title, url, type_):
        return f"{date}{type_}：{title}\n{url}"

    msg = ""
    for i in info["data"]:
        msg = msg + dtut(i["date"], i["title"], i["url"], i["class"]) + "\n"
    return msg
