from .... import *


@pytest.mark.skipif('get_tuilan_articles' not in dir(), reason='无api可用')
@pytest.mark.skipif(not Config.jx3api_globaltoken, reason="无apitoken时不测试")
def test_user():
    import src.plugins.jx3.user
    func = src.plugins.jx3.user.jx3_player

    def finish(msg: str):
        assert '25523361' in msg # uid
    mc = MessageCallback(cb_finish=finish)
    raw_matcher = src.plugins.jx3.user.jx3_cmd_roleInfo
    src.plugins.jx3.user.jx3_cmd_roleInfo = mc
    event = SFGroupMessageEvent()
    event.message = obMessage("角色信息 唯满侠 步龄")
    args = Jx3Arg.arg_factory(raw_matcher, event)
    task = func(event, args)
    asyncio.run(task)
    mc.check_counter()
