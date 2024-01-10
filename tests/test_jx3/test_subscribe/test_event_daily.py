from ... import *
from src.tools.dep.common_api.SubscribeRegister.events import *


def test_event_daily_plain_text():
    event = SFGroupMessageEvent()
    date = DateTime().tostring(DateTime.Format.YMD)
    content = PlainTxtDailyMessage(date, event.group_id, SubjectCron('* * * * *', '测试日常'))
    result = asyncio.run(content.get_message())

    assert '星期' in result
