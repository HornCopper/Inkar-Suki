from ... import *


def test_recruit():
    import src.plugins.jx3.recruit
    func = src.plugins.jx3.recruit.jx3_recruit

    def handle_finish(msg: str):
        if 'Token不正确哦' in str(msg):
            return
        assert False, f'fail run:{msg}'
    mc = MessageCallback(handle_finish)

    src.plugins.jx3.recruit.jx3_cmd_recruit = mc
    state = dict()
    from src.plugins.jx3.bind import server_bind

    event = SFGroupMessageEvent()
    server_bind(event.group_id, '双梦')
    task = func(state, event, obMessage('x 武狱黑牢'))
    asyncio.run(task)
    mc.check_counter()
    server_bind(event.group_id, '')
