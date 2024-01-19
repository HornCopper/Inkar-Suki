from src.tools.dep import *
notice_cmd_fetch_article_adopt = on_command(
    "技改",
    aliases={"技改", "武学", "武学调整"},
    priority=5,
    description='获取技改公告',
    catalog=permission.jx3.common.event.notice,
    example=[
        Jx3Arg(Jx3ArgsType.string, default=None, alias='标题'),
        Jx3Arg(Jx3ArgsType.string, default='技改', alias='栏目[不填]'),
    ],
    document='''查询技改的截图'''
)

notice_cmd_fetch_article_notice = on_command(
    "公告",
    aliases={"近期公告"},
    priority=5,
    description='获取公告',
    catalog=permission.jx3.common.event.notice,
    example=[
        Jx3Arg(Jx3ArgsType.string, default=None, alias='标题'),
        Jx3Arg(Jx3ArgsType.string, default='公告', alias='栏目[不填]'),
    ],
    document='''查询公告的截图'''
)

notice_cmd_fetch_article_news = on_command(
    "新闻",
    aliases={"新闻", "宣传", "近期新闻"},
    priority=5,
    description='获取新闻公告',
    catalog=permission.jx3.common.event.notice,
    example=[
        Jx3Arg(Jx3ArgsType.string, default=None, alias='标题'),
        Jx3Arg(Jx3ArgsType.string, default='新闻', alias='栏目[不填]'),
    ],
    document='''查询新闻的截图'''
)

notice_cmd_fetch_article_activity = on_command(
    "活动",
    aliases={"活动", "近期活动", "动态"},
    priority=5,
    description='获取活动公告',
    catalog=permission.jx3.common.event.notice,
    example=[
        Jx3Arg(Jx3ArgsType.string, default=None, alias='标题'),
        Jx3Arg(Jx3ArgsType.string, default='活动', alias='栏目[不填]'),
    ],
    document='''查询活动的截图'''
)

notice_cmd_fetch_article_update = on_command(
    "更新",
    aliases={"版本", "维护"},
    priority=5,
    description='获取更新',
    catalog=permission.jx3.common.event.notice,
    example=[
        Jx3Arg(Jx3ArgsType.string, default='更新', alias='标题'),
        Jx3Arg(Jx3ArgsType.string, default='公告', alias='栏目[不填]'),
    ],
    document='''查询公告的截图'''
)

@notice_cmd_fetch_article_adopt.handle()
@notice_cmd_fetch_article_notice.handle()
@notice_cmd_fetch_article_news.handle()
@notice_cmd_fetch_article_activity.handle()
@notice_cmd_fetch_article_update.handle()
async def notice_fetch_article_handler(event: GroupMessageEvent, args: list[Any] = Depends(Jx3Arg.arg_factory)):
    arg_title, arg_cata = args
    pass_args = (arg_cata, arg_title)
    result = await notice_fetch_common(pass_args)
    return await notice_cmd_fetch_article_adopt.send(result)


async def notice_fetch_common(args: list[Any]):
    arg_cata, arg_title = args
    item = await Jx3TuilanNoticeFactory.getNotice(arg_cata, filter=arg_title)
    if item.err_msg:
        return f'获取文章失败了:{item.err_msg}'
    content = item.document.html
    img = await generate_by_raw_html(content, name=f'notice_fetch_article@{arg_cata}')
    return ms.image(Path(img).as_uri())
