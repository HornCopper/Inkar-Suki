from __future__ import annotations
from src.tools.dep import *





async def get_jx3_article_raw(url: str):
    content = await get_content(url, proxy=proxies)
    data = json.loads(content[7:-2].decode())
    result = data.get('data') or {}
    items = result.get('list') if isinstance(result, dict) else result
    _ = result.get('total') if isinstance(result, dict) else 0
    return items


async def get_jx3_articles(catalog: str = '技改', pageIndex: int = 0):
    url = get_tuilan_articles(catalog, pageIndex)
    return await get_jx3_article_raw(url)


class Jx3ArticleDetail:
    '''TODO 解析技改各个心法的变化数据形成视图'''
    db: dict[str, Jx3ArticleDetail] = filebase_database.Database(
        f'{bot_path.common_data_full}jx3-article').value

    def __init__(self) -> None:
        self.id = ''


async def get_jx3_article_detail(item: dict):
    url = get_tuilan_detail(item)
    result = await get_jx3_article_raw(url)
    return result[0]


async def announce_by_jx3api():
    final_url = f"{Config.jx3api_link}/view/web/news/announce?robot={bot}&token={token}"
    data = await get_api(final_url, proxy=proxies)
    return data["data"]["url"]
