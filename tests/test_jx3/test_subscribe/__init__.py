from ... import *

group = random.Random().randrange(int(1e7), int(1e8))
import src.plugins.jx3.subscribe

def test_subscribe():
    def check_sub(raw: str):
        assert '已开启' in raw
    mc = MessageCallback(cb_finish=check_sub)
    src.plugins.jx3.subscribe.jx3_cmd_subscribe = mc
    func = src.plugins.jx3.subscribe.jx3_subscribe
    event = SFGroupMessageEvent(group_id=group)
    mc.tag = '玄晶'
    task = func(event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


def test_duplicate_subscripe():
    def check_unsub(raw: str):
      assert '已经订阅了' in raw
    
    mc = MessageCallback(cb_finish=check_unsub)
    src.plugins.jx3.subscribe.jx3_cmd_subscribe = mc
    mc.tag = '玄晶'
    func = src.plugins.jx3.subscribe.jx3_subscribe
    event = SFGroupMessageEvent(group_id=group)
    task = func(event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

def test_notexist_subscripe():
    def check_unsub(raw: str):
      assert '很奇怪' in raw
    
    mc = MessageCallback(cb_finish=check_unsub)
    src.plugins.jx3.subscribe.jx3_cmd_subscribe = mc
    mc.tag = '不存在'
    func = src.plugins.jx3.subscribe.jx3_subscribe
    event = SFGroupMessageEvent(group_id=group)
    task = func(event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

def test_unsubscribe():
    def check_sub(raw: str):
        assert '已开启' in raw
    mc = MessageCallback(cb_finish=check_sub)
    src.plugins.jx3.subscribe.jx3_cmd_unsubscribe = mc
    func = src.plugins.jx3.subscribe.jx3_unsubscribe
    event = SFGroupMessageEvent(group_id=group)
    mc.tag = '玄晶'
    task = func(event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


    def check_sub(raw: str):
        assert '尚未订阅' in raw
    mc = MessageCallback(cb_finish=check_sub)
    src.plugins.jx3.subscribe.jx3_cmd_unsubscribe = mc
    func = src.plugins.jx3.subscribe.jx3_unsubscribe
    event = SFGroupMessageEvent(group_id=group)
    mc.tag = '玄晶'
    task = func(event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()