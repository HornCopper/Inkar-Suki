from . import *


def test_recruit():
    import src.plugins.jx3
    jx3_recruit = src.plugins.jx3.jx3_recruit

    def handle_finish(msg: str):
        if 'Token不正确哦' in str(msg):
            return
        assert False, f'fail run:{msg}'

    def handle_send(msg: str):
        assert len(msg) > 10
    src.plugins.jx3.recruit = MessageCallback(handle_finish, handle_send)
    state = dict()
    state['server'] = '双梦'
    event = SFGroupMessageEvent()
    task = jx3_recruit(state, event, obMessage('x 武狱黑牢'))
    asyncio.run(task)
