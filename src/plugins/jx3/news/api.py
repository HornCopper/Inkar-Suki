from src.tools.dep import *


async def news_():
    full_link = f"{Config.jx3api_link}/data/web/news/allnews?limit=5&token={token}"
    info = await get_api(full_link, proxy=proxies)

    def dtut(date, title, url, type_):
        return f"{date}{type_}：{title}\n{url}"
    msg = ""
    for i in info["data"]:
        msg = msg + dtut(i["date"], i["title"], i["url"], i["type"]) + "\n"
    return msg
