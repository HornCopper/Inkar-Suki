from .... import *

@pytest.mark.skipif(not Config.jx3_token, reason="无token时不测试")
def test_records():
    import src.plugins.jx3.arena
    func = src.plugins.jx3.arena.jx3_arena_records

    mc = MessageCallback()
    src.plugins.jx3.arena.jx3_arena_records = mc
    event = SFGroupMessageEvent()
    event.message = obMessage("幽月轮 凉夜话雨")
    task = func(event, Jx3Arg.arg_factory(src.plugins.jx3.arena.jx3_cmd_arena_records, event))
    asyncio.run(task)
    mc.check_counter()