from ... import *


@pytest.mark.skipif('Jx3TuilanNoticeFactory' not in dir(), reason='无api可用')
def test_fetch_adopt():
    task = Jx3TuilanNoticeFactory.getNotice('新闻')
    result = asyncio.run(task)
    assert result.document.html

    task = Jx3TuilanNoticeFactory.getNotice('公告')
    result = asyncio.run(task)
    assert result.document.html
    pass