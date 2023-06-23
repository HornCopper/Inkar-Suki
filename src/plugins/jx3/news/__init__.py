from .api import *

news = on_command("jx3_news", aliases={"新闻"}, priority=5)
@news.handle()
async def _():
    '''
    获取剑网3近期新闻：

    Example：-新闻
    '''
    await news.finish(await news_())
