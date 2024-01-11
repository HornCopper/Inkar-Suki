from src.tools.dep import *


async def get_jx3_article(catalog: str = '技改', pageIndex: int = 0):
    url = get_tuilan_article(catalog, pageIndex)
    data = await get_api(url, proxy=proxies)
    result = data.get('data') or {}
    items = result.get('list')
    _ = result.get('total')
    return items


async def announce_by_jx3api():
    final_url = f"{Config.jx3api_link}/view/web/news/announce?robot={bot}&token={token}"
    data = await get_api(final_url, proxy=proxies)
    return data["data"]["url"]
