from .api import *

news = on_command("jx3_news", aliases={"新闻"}, force_whitespace=True, priority=5)


@news.handle()
async def _(args: Message = CommandArg()):
    """
    获取剑网3近期新闻：

    Example：-新闻
    """
    if args.extract_plain_text() != "":
        return
    r = await news_()
    # if isinstance(r, GloConfigException):
    #     await r.finish(news)
    await news.finish(r)
