from .... import *


@pytest.mark.skipif(not Config.jx3_token, reason="无token时不测试")
def test_user_property():
    import src.plugins.jx3.user
    func = src.plugins.jx3.user.jx3_addritube

    def finish(msg: str):
        assert 'file://' in msg, f'image generate fail:{msg}.'
    mc = MessageCallback(cb_finish=finish)
    src.plugins.jx3.user.jx3_cmd_roleInfo = mc
    event = SFGroupMessageEvent()
    task = func(event, obMessage('唯满侠 步龄'))
    asyncio.run(task)
    mc.check_counter()


@pytest.mark.skipif(not Config.jx3_token, reason="无token时不测试")
def test_user_property_v2():
    import src.plugins.jx3.user
    func = src.plugins.jx3.user.jx3_addritube_v2

    def finish(msg: str):
        assert 'file://' in msg, f'image generate fail:{msg}.'
    mc = MessageCallback(cb_finish=finish)
    src.plugins.jx3.user.jx3_cmd_addritube_v2 = mc
    event = SFGroupMessageEvent()
    task = func(event, obMessage('唯满侠 步龄'))
    asyncio.run(task)
    mc.check_counter()
