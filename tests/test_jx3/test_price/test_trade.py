from ... import *

import src.plugins.jx3
from src.plugins.jx3.price_goods.lib import coin, Golds
from src.plugins.jx3.price_goods import v1


def test_trade_gold():
    Gold = Golds.Gold
    assert Gold(1).__repr__() == "1 铜"
    assert Gold(200).__repr__() == "2 银"
    assert Gold(80000).__repr__() == "8 金"
    assert Gold(88800).__repr__() == "8 金 88 银"
    assert Gold(100888800).__repr__() == "1 砖 88 金 88 银"
    assert Gold(100008800).__repr__() == "1 砖 88 银"
    assert Gold(100000000).__repr__() == "1 砖"
    assert len(str(Gold(100888800))) > 1e3, "image of b64 should be very long"

    t = f"98 <img src=\"{coin.brickl}\" /> 12 <img src=\"{coin.goldl}\" /> 34 <img src=\"{coin.silverl}\" /> 56 <img src=\"{coin.copperl}\" />"
    assert str(Gold(9800123456)) == t, "convert image maybe wrong"


def test_trade_record():
    mc = MessageCallback()
    v1.jx3_cmd_trade = mc

    jx3_trade = src.plugins.jx3.jx3_trade
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = "唯满侠 五行石"
    task = jx3_trade(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


def test_default_server():
    mc = MessageCallback()
    v1.jx3_cmd_trade = mc

    jx3_trade = src.plugins.jx3.jx3_trade
    state = {}
    event = SFGroupMessageEvent()
    from src.plugins.jx3.bind import server_bind
    server_bind(event.group_id, "唯满侠")

    mc.tag = "武技殊影图"
    task = jx3_trade(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()
    mc.tag = "武技殊影图 2"  # 第二页
    task = jx3_trade(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()
    server_bind(event.group_id, "")


def test_not_exist():
    def handle_finish(msg: str):
        assert "没有找到该物品" in msg, f"expected not exist , but get result:{msg}"

    def handle_send(msg: str):
        assert False, f"expected finish but get send:{msg}"
    mc = MessageCallback(cb_finish=handle_finish, cb_send=handle_send)
    v1.jx3_cmd_trade = mc

    jx3_trade = src.plugins.jx3.jx3_trade
    state = {}
    event = SFGroupMessageEvent()
    mc.tag = "唯满侠 不存在哈哈哈"
    task = jx3_trade(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


def test_trade_price():
    mc = MessageCallback()
    v1.jx3_cmd_trade = mc

    price_num_selected = src.plugins.jx3.price_num_selected
    state = {"id": ["5_47116"], "server": "唯我独尊"}  # 武技殊影图·上将
    event = SFGroupMessageEvent()

    task = price_num_selected(state, event, obMessage("0"))
    asyncio.run(task)
    mc.check_counter()


def test_trade_bound_good():

    import src.plugins.jx3

    w_tip = "bound goods should show alert."

    def cb_finish(msg: str):
        assert "绑定" in msg, w_tip

    def cb_send(msg: str):
        assert False, w_tip
    mc = MessageCallback(cb_finish=cb_finish, cb_send=cb_send)
    v1.jx3_cmd_trade = mc

    price_num_selected = src.plugins.jx3.price_num_selected
    state = {"id": ["5_24447"], "server": "唯我独尊"}  # 五行石五级（拾绑）

    event = SFGroupMessageEvent()

    task = price_num_selected(state, event, obMessage("0"))
    asyncio.run(task)
    mc.check_counter()


def test_goods_info_db():
    """
    test by run test_trade_record twice for load cache_file
    """
    test_trade_record()
