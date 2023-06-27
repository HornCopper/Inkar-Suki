from .... import *


def test_rank_qualifications():
    import src.plugins.jx3.rank
    func = src.plugins.jx3.rank.jx3_zlrank

    def finish(msg: str):
        assert 'file://' in msg, f'image generate fail:{msg}.'
    mc = MessageCallback(cb_finish=finish)
    src.plugins.jx3.rank.jx3_cmd_zlrank = mc
    event = SFGroupMessageEvent()
    task = func(event, obMessage('长歌'))
    asyncio.run(task)
    mc.check_counter()
