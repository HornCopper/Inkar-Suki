from ... import *


@pytest.mark.skipif('get_tuilan_articles' not in dir(), reason='无api可用')
@pytest.mark.skipif(not Config.jx3api_globaltoken, reason="无apitoken时不测试")
def test_user_property():
    import src.plugins.jx3.user.v2

    def finish(msg: str):
        assert 'file://' in msg, f'image generate fail:{msg}.'
    mc = MessageCallback(cb_finish=finish)
    src.plugins.jx3.user.v2.jx3_cmd_addritube_v2 = mc
    func = src.plugins.jx3.jx3_addritube_v2

    event = SFGroupMessageEvent(group_id=1120115)
    event.message = obMessage("属性 唯满侠 步龄")
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_addritube_v2, event)
    task = func(event, args)
    asyncio.run(task)
    mc.check_counter()

@pytest.mark.skipif('get_tuilan_articles' not in dir(), reason='无api可用')
@pytest.mark.skipif(not Config.jx3api_globaltoken, reason="无apitoken时不测试")
def test_user_property_v2():
    import src.plugins.jx3.user

    def finish(msg: str):
        assert 'file://' in msg, f'image generate fail:{msg}.'
    mc = MessageCallback(cb_finish=finish)
    src.plugins.jx3.user.v2.jx3_cmd_addritube_v2 = mc
    func = src.plugins.jx3.jx3_addritube_v2
    event = SFGroupMessageEvent()
    
    event.message = obMessage("属性 唯满侠 步龄")
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_addritube_v2, event)
    task = func(event, args)
    asyncio.run(task)
    mc.check_counter()
