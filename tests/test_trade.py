from . import *


def test_trade_record():
    import src.plugins.jx3
    jx3_trade = src.plugins.jx3.jx3_trade

    def handle_finish(msg: str):
        assert False, f'fail run:{msg}'

    def handle_send(msg: str):
        assert len(msg) > 10
    src.plugins.jx3.trade_ = MessageCallback(handle_finish, handle_send)
    state = dict()
    state['server'] = '双梦'
    event = SFGroupMessageEvent()
    task = jx3_trade(state, event, obMessage('唯满侠 五行石'))
    asyncio.run(task)
