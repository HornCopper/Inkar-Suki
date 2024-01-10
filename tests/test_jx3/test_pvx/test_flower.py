from ... import *


def test_flower_price():
    import src.plugins.jx3
    import src.plugins.jx3.flower
    func = src.plugins.jx3.flower.jx3_flower
    mc = MessageCallback()

    src.plugins.jx3.flower.jx3_cmd_flower = mc
    state = dict()
    event = SFGroupMessageEvent()
    event.message = obMessage('花 唯满侠')
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_flower, event)
    task = func(state, event, args)
    asyncio.run(task)
    mc.check_counter()

    event.message = obMessage('花 唯满侠 不存在地图')
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_flower, event)
    task = func(state, event, args)
    asyncio.run(task)
    mc.check_counter()
