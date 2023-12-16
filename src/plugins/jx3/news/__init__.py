from .api import *

news = on_command("jx3_news", aliases={"新闻"}, priority=5)


@news.handle()
async def _():
    """
    获取剑网3近期新闻：

    Example：-新闻
    """
    r = await news_()
    # if isinstance(r, GloConfigException):
    #     return await r.finish(news)
    return await news.finish(r)
