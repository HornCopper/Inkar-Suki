from ... import *

import src.plugins.jx3
import src.plugins.jx3.price_goods

def test_trade_gold():
    from src.plugins.jx3.price_goods import Gold
    assert Gold(1).__repr__() == '1 铜'
    assert Gold(200).__repr__() == '2 银'
    assert Gold(80000).__repr__() == '8 金'
    assert Gold(88800).__repr__() == '8 金 88 银'
    assert Gold(100888800).__repr__() == '1 砖 88 金 88 银'
    assert Gold(100008800).__repr__() == '1 砖 88 银'
    assert Gold(100000000).__repr__() == '1 砖'
    assert len(str(Gold(100888800))) > 1e3, 'image of b64 should be very long'

    from src.plugins.jx3.price_goods import coin
    t = f'98 <img src="{coin.brickl}" /> 12 <img src="{coin.goldl}" /> 34 <img src="{coin.silverl}" /> 56 <img src="{coin.copperl}" />'
    assert str(Gold(9800123456)) == t, 'convert image maybe wrong'


def test_trade_record():
    mc = MessageCallback()
    src.plugins.jx3.price_goods.jx3_cmd_trade = mc

    jx3_trade = src.plugins.jx3.jx3_trade
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = '唯满侠 五行石'
    task = jx3_trade(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

    mc.tag = '武技殊影图'
    task = jx3_trade(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


def test_trade_price():
    mc = MessageCallback()
    src.plugins.jx3.price_goods.jx3_cmd_trade = mc

    price_num_selected = src.plugins.jx3.price_num_selected
    state = {'id': ['5_47116'], 'server': '唯我独尊'}  # 武技殊影图·上将
    event = SFGroupMessageEvent()

    task = price_num_selected(state, event, obMessage('0'))
    asyncio.run(task)
    mc.check_counter()


def test_trade_bound_good():

    import src.plugins.jx3

    w_tip = 'bound goods should show alert.'
    def cb_finish(msg: str):
        assert '绑定' in msg, w_tip

    def cb_send(msg: str):
        assert False, w_tip
    mc = MessageCallback(cb_finish=cb_finish, cb_send=cb_send)
    src.plugins.jx3.price_goods.jx3_cmd_trade = mc

    price_num_selected = src.plugins.jx3.price_num_selected
    state = {'id': ['5_24447'], 'server': '唯我独尊'}  # 五行石五级（拾绑）

    event = SFGroupMessageEvent()

    task = price_num_selected(state, event, obMessage('0'))
    asyncio.run(task)
    mc.check_counter()


def test_goods_info_db():
    '''
    test by run test_trade_record twice for load cache_file
    '''
    test_trade_record()
