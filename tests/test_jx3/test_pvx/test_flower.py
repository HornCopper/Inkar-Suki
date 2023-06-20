from ... import *


def test_flower_price():
    import src.plugins.jx3.flower
    func = src.plugins.jx3.flower.jx3_flower
    mc = MessageCallback()

    src.plugins.jx3.flower.jx3_cmd_flower = mc
    state = dict()
    event = SFGroupMessageEvent()
    task = func(state, event, obMessage('唯满侠'))
    asyncio.run(task)
    mc.check_counter()
