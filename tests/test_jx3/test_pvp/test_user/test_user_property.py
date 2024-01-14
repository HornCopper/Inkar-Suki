from .... import *


@pytest.mark.skipif('get_tuilan_articles' not in dir(), reason='无api可用')
@pytest.mark.skipif(not Config.jx3api_globaltoken, reason="无apitoken时不测试")
def test_user_property():
    import src.plugins.jx3.user
    func = src.plugins.jx3.user.jx3_addritube

    def finish(msg: str):
        assert 'file://' in msg, f'image generate fail:{msg}.'
    mc = MessageCallback(cb_finish=finish)
    raw_matcher = src.plugins.jx3.user.jx3_cmd_addritube
    src.plugins.jx3.user.jx3_cmd_addritube = mc

    event = SFGroupMessageEvent(group_id=1120115)
    event.message = obMessage("属性 唯满侠 步龄")
    args = Jx3Arg.arg_factory(raw_matcher, event)
    task = func(event, args)
    asyncio.run(task)
    mc.check_counter()

@pytest.mark.skipif('get_tuilan_articles' not in dir(), reason='无api可用')
@pytest.mark.skipif(not Config.jx3api_globaltoken, reason="无apitoken时不测试")
def test_user_property_v2():
    import src.plugins.jx3.user
    func = src.plugins.jx3.user.jx3_addritube_v2

    def finish(msg: str):
        assert 'file://' in msg, f'image generate fail:{msg}.'
    mc = MessageCallback(cb_finish=finish)
    raw_matcher = src.plugins.jx3.user.jx3_cmd_addritube_v2
    src.plugins.jx3.user.jx3_cmd_addritube_v2 = mc
    event = SFGroupMessageEvent()
    
    event.message = obMessage("属性 唯满侠 步龄")
    args = Jx3Arg.arg_factory(raw_matcher, event)
    task = func(event, args)
    asyncio.run(task)
    mc.check_counter()
