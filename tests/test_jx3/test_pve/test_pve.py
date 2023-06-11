from ... import *


def test_recruit():
    import src.plugins.jx3.recruit
    jx3_recruit = src.plugins.jx3.recruit.jx3_recruit

    def handle_finish(msg: str):
        if 'Token不正确哦' in str(msg):
            return
        assert False, f'fail run:{msg}'
    mc = MessageCallback(handle_finish)
    
    src.plugins.jx3.recruit.jx3_cmd_recruit = mc
    state = dict()
    state['server'] = '双梦'
    event = SFGroupMessageEvent()
    task = jx3_recruit(state, event, obMessage('x 武狱黑牢'))
    asyncio.run(task)
    mc.check_counter()
