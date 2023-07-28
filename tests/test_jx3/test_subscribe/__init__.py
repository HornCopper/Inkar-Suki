import src.plugins.jx3.subscribe
from ... import *

rnd_group = random.Random().randrange(int(1e7), int(1e8))


def test_subscribe():
    def check_sub(raw: str):
        assert "已开启" in raw
    func = src.plugins.jx3.subscribe.get_jx3_subscribe
    event = SFGroupMessageEvent(group_id=rnd_group)
    task = func(event, obMessage("大攻防"))
    result = asyncio.run(task)
    msg = result[2]
    check_sub(msg)


def test_duplicate_subscripe():
    def check_sub(raw: str):
        assert "已经订阅了" in raw

    func = src.plugins.jx3.subscribe.get_jx3_subscribe
    event = SFGroupMessageEvent(group_id=rnd_group)
    task = func(event, obMessage("玄晶"))
    result = asyncio.run(task)
    msg = result[2]
    check_sub(msg)


def test_notexist_subscripe():
    def check_unsub(raw: str):
        assert "很奇怪" in raw

    func = src.plugins.jx3.subscribe.get_jx3_unsubscribe
    event = SFGroupMessageEvent(group_id=rnd_group)
    task = func(event, obMessage("不存在"))
    result = asyncio.run(task)
    msg = result[2]
    check_unsub(msg)


def test_unsubscribe():
    def check_unsub(raw: str):
        assert "已开启" in raw
    func = src.plugins.jx3.subscribe.get_jx3_unsubscribe
    event = SFGroupMessageEvent(group_id=rnd_group)
    task = func(event, obMessage("玄晶"))
    result = asyncio.run(task)
    msg = result[2]
    check_unsub(msg)

    def check_unsub(raw: str):
        assert "尚未订阅" in raw
    func = src.plugins.jx3.subscribe.get_jx3_unsubscribe
    event = SFGroupMessageEvent(group_id=rnd_group)
    task = func(event, obMessage("玄晶"))
    result = asyncio.run(task)
    msg = result[2]
    check_unsub(msg)
