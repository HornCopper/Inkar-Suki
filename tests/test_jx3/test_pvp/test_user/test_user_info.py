from .... import *


@pytest.mark.skipif(not Config.jx3api_globaltoken, reason="无apitoken时不测试")
def test_user():
    import src.plugins.jx3.user
    func = src.plugins.jx3.user.jx3_player

    def finish(msg: str):
        assert "file://" in msg, f"image generate fail:{msg}."
    mc = MessageCallback(cb_finish=finish)
    src.plugins.jx3.user.jx3_cmd_roleInfo = mc
    event = SFGroupMessageEvent()
    task = func(event, obMessage("唯满侠 步龄"))
    asyncio.run(task)
    mc.check_counter()
