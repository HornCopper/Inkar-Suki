from ... import *

@pytest.mark.skip(reason='pull.j3cx.com网站已无不可用，返回太慢')
def test_serendipity():
    import src.plugins.jx3
    import src.plugins.jx3.dungeon.cd
    func = src.plugins.jx3.dungeon.cd.jx3_rare_gain

    def finish(msg: str):
        pass
    mc = MessageCallback(cb_finish=finish)
    src.plugins.jx3.dungeon.cd.jx3_cmd_jx3_rare_gain = mc
    event = SFGroupMessageEvent()
    mc.tag = '掉落 太一玄晶'
    event.message = obMessage(mc.tag)
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_jx3_rare_gain, event)
    task = func(event, args)

    asyncio.run(task)
    mc.check_counter()
