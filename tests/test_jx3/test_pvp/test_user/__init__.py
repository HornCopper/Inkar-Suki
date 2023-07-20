from .... import *
<<<<<<< HEAD
import pytest
=======
>>>>>>> 14476fd734b56a647406dd0ab8bdf37d6f6707a0

@pytest.mark.skip('没有token')
def test_user():
    import src.plugins.jx3.user
    func = src.plugins.jx3.user.jx3_player

    def finish(msg: str):
        assert 'file://' in msg, f'image generate fail:{msg}.'
    mc = MessageCallback(cb_finish=finish)
    src.plugins.jx3.user.jx3_cmd_roleInfo = mc
    event = SFGroupMessageEvent()
    task = func(event, obMessage('唯满侠 步龄'))
    asyncio.run(task)
    mc.check_counter()
