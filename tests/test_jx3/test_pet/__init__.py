from ... import *
import src.plugins.jx3.pet


def test_pet():
    def cb_finish(msg: str):
        assert len(msg) > 10
    mc = MessageCallback(cb_finish=cb_finish)
    src.plugins.jx3.pet.jx3_cmd_pet = mc

    func = src.plugins.jx3.jx3_pet
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = "静静"
    task = func(state, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

    mc.tag = "小"
    task = func(state, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()
