from ... import *
from src.tools.dep.common_api.SubscribeRegister.events import *


@pytest.mark.skipif('Jx3TuilanNoticeFactory' not in dir(), reason='无api可用')
def test_event_daily_plain_text():
    event = SFGroupMessageEvent()
    event.group_id = 101100101
    date = DateTime().tostring(DateTime.Format.YMD)
    from src.plugins.jx3.bind import server_bind
    server_bind(event.group_id, '唯满侠')
    content = PlainTxtDailyMessage(date, event.group_id, SubjectCron('* * * * *', '测试日常'))
    result = asyncio.run(content.get_message())

    assert '星期' in result
