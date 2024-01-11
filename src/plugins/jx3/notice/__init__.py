import bs4
from .api import *

announce = on_command("jx3_announce", aliases={"维护公告", "更新公告", "公告", "更新"}, priority=5)


@announce.handle()
async def _(event: GroupMessageEvent):
    """
    获取维护公告的图片：

    Example：-维护公告
    """
    url = await announce_by_jx3api()
    return await announce.finish(ms.image(url))

notice_cmd_fetch_article_adopt = on_command(
    "技改",
    aliases={"技改", "武学", "武学调整"},
    priority=5,
    description='获取技改公告',
    catalog=permission.jx3.common.event.notice,
    example=[
        Jx3Arg(Jx3ArgsType.string, default='技改', alias='分类名称'),
    ],
    document='''查询技改、新闻、公告的截图'''
)


@notice_cmd_fetch_article_adopt.handle()
async def notice_fetch_article_adopt(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_cata, = args
    items = await get_jx3_articles(arg_cata)
    if not items:
        return notice_cmd_fetch_article_adopt.finish('获取文章列表失败了')
    item = await get_jx3_article_detail(items[0])
    if not item:
        return notice_cmd_fetch_article_adopt.finish('获取文章内容失败了')
    content = item.get('content')
    title = item.get('title')
    date = DateTime(int(item.get('updatetime'))*1e3).tostring(DateTime.Format.DEFAULT)
    content = f'<h1 style="text-align:center">{title}</h1><h2 style="text-align:center">{date}</h2><div>{content}</div>'  # TODO 使用模板
    doc = bs4.BeautifulSoup(content)
    # 移除无效项
    [ele.extract() for ele in doc.find_all('p') if len(ele.text) < 2]
    content = doc.prettify()
    content = f'<section style="width:800px">{content}</section>'
    img = await generate_by_raw_html(content, name='notice_fetch_article_adopt')
    return await notice_cmd_fetch_article_adopt.send(ms.image(Path(img).as_uri()))
