from ... import *
from . import rnd_group


def test_subscribe_schedule():
    def check_sub(raw: str):
        assert '已开启' in raw
    func = src.plugins.jx3.subscribe.get_jx3_subscribe
    event = SFGroupMessageEvent(group_id=rnd_group)
    task = func(event, ['大攻防', None])
    result = asyncio.run(task)
    msg = result[2]
    check_sub(msg)


def test_subscribe_lower():
    def check_sub(raw: str):
        assert '已开启' in raw
    func = src.plugins.jx3.subscribe.get_jx3_subscribe
    event = SFGroupMessageEvent(group_id=rnd_group)
    task = func(event, ['世界BoSs', None])
    result = asyncio.run(task)
    msg = result[2]
    check_sub(msg)
