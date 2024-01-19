from .... import *

@pytest.mark.skipif('Jx3TuilanNoticeFactory' not in dir(), reason='无api可用')
@pytest.mark.skipif(not Config.jx3api_globaltoken, reason="无token时不测试")
def test_records():
    from src.plugins.jx3 import arena
    func = src.plugins.jx3.arena.jx3_arena_records

    mc = MessageCallback()
    arena.jx3_cmd_arena_records = mc

    event = SFGroupMessageEvent()
    event.message = obMessage("战绩 幽月轮 凉夜话雨")
    task = func(event, Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_arena_records, event))
    asyncio.run(task)
    mc.check_counter()
