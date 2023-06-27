from ... import *


def test_serendipity():
    import src.plugins.jx3.dungeon.xuanjing
    func = src.plugins.jx3.dungeon.xuanjing.jx3_rare_gain

    def finish(msg: str):
        pass
    mc = MessageCallback(cb_finish=finish)
    src.plugins.jx3.dungeon.xuanjing.jx3_cmd_jx3_rare_gain = mc
    event = SFGroupMessageEvent()
    task = func(event, obMessage('唯满侠 太一玄晶'))
    asyncio.run(task)
    mc.check_counter()
