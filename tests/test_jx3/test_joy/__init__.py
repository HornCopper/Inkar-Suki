from ... import *
from src.plugins.jx3 import jxjoy


def test_saohua():
    def cb_finish(msg: str):
        assert len(msg) > 10
    mc = MessageCallback(cb_finish=cb_finish)
    jxjoy.jx3_cmd_saohua_random = mc

    func = jxjoy.jx3_saohua_random
    task = func()
    asyncio.run(task)
    mc.check_counter()


def test_tiangou():
    def cb_finish(msg: str):
        assert len(msg) > 10
    mc = MessageCallback(cb_finish=cb_finish)
    jxjoy.jx3_cmd_saohua_tiangou = mc

    func = jxjoy.jx3_saohua_tiangou
    task = func()
    asyncio.run(task)
    mc.check_counter()