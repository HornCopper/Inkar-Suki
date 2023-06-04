from . import *


def test_trade_record():
    import src.plugins.jx3
    mc = MessageCallback()
    src.plugins.jx3.trade_ = mc

    jx3_trade = src.plugins.jx3.jx3_trade
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = '唯满侠 五行石'
    task = jx3_trade(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

    mc.tag = '五行石'
    task = jx3_trade(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()
