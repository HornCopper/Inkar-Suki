from ... import *


def test_fetch_adopt():
    mc = MessageCallback()
    import src.plugins.jx3.notice
    raw_matcher = src.plugins.jx3.notice.notice_cmd_fetch_article_adopt
    func = src.plugins.jx3.notice.notice_fetch_article_adopt
    src.plugins.jx3.notice.notice_cmd_fetch_article_adopt = mc
    event = SFGroupMessageEvent()
    mc.tag = '技改'
    event.message = obMessage(mc.tag)

    args = Jx3Arg.arg_factory(raw_matcher, event)
    task = func(event, args)
    asyncio.run(task)
    mc.check_counter()
