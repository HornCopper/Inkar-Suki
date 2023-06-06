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


def test_trade_bound_good():

    import src.plugins.jx3
    def cb_finish(msg: str):
        assert '绑定' in msg, w_tip

    def cb_send(msg: str):
        assert False, w_tip
    mc = MessageCallback(cb_finish=cb_finish,cb_send=cb_send)
    src.plugins.jx3.trade_ = mc

    price_num_selected = src.plugins.jx3.price_num_selected
    state = {'id': ['5_24447'], 'server': '唯我独尊'}  # 五行石五级（拾绑）
    w_tip = 'bound goods should show alert.'

    event = SFGroupMessageEvent()

    task = price_num_selected(state, event, obMessage('0'))
    asyncio.run(task)
    mc.check_counter()

def test_goods_info_db():
    '''
    test by run test_trade_record twice for load cache_file
    '''
    test_trade_record()