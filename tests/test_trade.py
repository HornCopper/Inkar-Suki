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


def test_trade_price():

    import src.plugins.jx3
    mc = MessageCallback()
    src.plugins.jx3.trade_ = mc

    price_num_selected = src.plugins.jx3.price_num_selected
    state = {'id': ['5_24428'], 'server': '唯我独尊'}  # 五行石六级
    event = SFGroupMessageEvent()

    task = price_num_selected(state, event, obMessage('0'))
    asyncio.run(task)
    mc.check_counter()

