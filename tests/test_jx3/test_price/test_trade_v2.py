from ... import *

import src.plugins.jx3
from src.plugins.jx3.price_goods import v2


def test_trade_record():
    mc = MessageCallback()
    v2.jx3_cmd_trade2 = mc

    jx3_trade = src.plugins.jx3.jx3_trade2
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = '唯满侠 五行石'
    task = jx3_trade(mc, state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


def test_default_server():
    mc = MessageCallback()
    v2.jx3_cmd_trade2 = mc

    jx3_trade = src.plugins.jx3.jx3_trade2
    state = {}
    event = SFGroupMessageEvent()
    from src.plugins.jx3.bind import server_bind
    server_bind(event.group_id, '唯满侠')

    mc.tag = '武技殊影图'
    task = jx3_trade(mc, state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()
    mc.tag = '武技殊影图 2'  # 第二页
    task = jx3_trade(mc, state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()
    server_bind(event.group_id, '')


def jx3_trade_favoritest():
    mc = MessageCallback()
    v2.jx3_cmd_favouritest = mc

    func = src.plugins.jx3.jx3_trade_favoritest
    state = {}
    event = SFGroupMessageEvent()
    mc.tag = '唯满侠'
    task = func(mc, state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


def test_not_exist():
    def handle_finish(msg: str):
        assert '没有找到该物品' in msg, f'expected not exist , but get result:{msg}'

    def handle_send(msg: str):
        assert False, f'expected finish but get send:{msg}'
    mc = MessageCallback(cb_finish=handle_finish, cb_send=handle_send)
    v2.jx3_cmd_trade2 = mc

    jx3_trade = src.plugins.jx3.jx3_trade2
    state = {}
    event = SFGroupMessageEvent()
    mc.tag = '唯满侠 不存在哈哈哈'
    task = jx3_trade(mc, state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


def test_trade_price():
    mc = MessageCallback()
    v2.jx3_cmd_trade2 = mc

    price_num_selected = src.plugins.jx3.price_num_selected2
    state = {'id': ['5_47116'], 'server': '唯我独尊'}  # 武技殊影图·上将
    event = SFGroupMessageEvent()

    task = price_num_selected(state, event, obMessage('1'))
    asyncio.run(task)
    mc.check_counter()

    state = {'id': ['5_47116'], 'server': '唯我独尊'}  # 武技殊影图·上将
    task = price_num_selected(state, event, obMessage('1'))
    asyncio.run(task)
    mc.check_counter()


def test_goods_info_db():
    '''
    test by run test_trade_record twice for load cache_file
    '''
    test_trade_record()


def test_goods_level():
    mc = MessageCallback()
    v2.jx3_cmd_trade2 = mc

    jx3_trade = src.plugins.jx3.jx3_trade2
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = '唯满侠 无封裤'
    task = jx3_trade(mc, state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

    price_num_selected = src.plugins.jx3.price_num_selected2
    state = {'id': ['7_94556'], 'server': '唯我独尊'}  # 无封裤（12100）
    event = SFGroupMessageEvent()

    task = price_num_selected(state, event, obMessage('1'))
    asyncio.run(task)
    mc.check_counter()


@pytest.mark.skip('运行时间过长')
def test_price_updater():
    func = src.plugins.jx3.refresh_favoritest_goods_current_price
    task = func()
    asyncio.run(task)


def test_trade_wucai_price():
    mc = MessageCallback()
    v2.jx3_cmd_trade2 = mc
    price_num_selected = src.plugins.jx3.price_num_selected2
    state = {'id': ['5_12891'], 'server': '唯我独尊'}  # 彩·灵根·灭气·激流(叁)
    event = SFGroupMessageEvent()

    task = price_num_selected(state, event, obMessage('1'))
    asyncio.run(task)
    mc.check_counter()
