from ... import *
from . import rnd_group

def test_subscribe_schedule():
    def check_sub(raw: str):
        assert '已开启' in raw
    mc = MessageCallback(cb_finish=check_sub)
    src.plugins.jx3.subscribe.jx3_cmd_subscribe = mc
    func = src.plugins.jx3.subscribe.jx3_subscribe
    event = SFGroupMessageEvent(group_id=rnd_group)
    mc.tag = '大攻防'
    task = func(event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

def test_subscribe_lower():
    def check_sub(raw: str):
        assert '已开启' in raw
    mc = MessageCallback(cb_finish=check_sub)
    src.plugins.jx3.subscribe.jx3_cmd_subscribe = mc
    func = src.plugins.jx3.subscribe.jx3_subscribe
    event = SFGroupMessageEvent(group_id=rnd_group)
    mc.tag = '世界BoSs'
    task = func(event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()
