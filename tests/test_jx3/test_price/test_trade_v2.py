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

    task = price_num_selected(state, event, obMessage('0'))
    asyncio.run(task)
    mc.check_counter()

    state = {'id': ['6_34768'], 'server': '唯我独尊'}  # 度飞囊
    task = price_num_selected(state, event, obMessage('0'))
    asyncio.run(task)
    mc.check_counter()


def test_goods_info_db():
    '''
    test by run test_trade_record twice for load cache_file
    '''
    test_trade_record()
