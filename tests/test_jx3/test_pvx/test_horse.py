
from ... import *


def test_horse_loader():
    import src.plugins.jx3.horse.v2
    result = asyncio.run(src.plugins.jx3.horse.v2.get_horse_reporter('唯我独尊'))
    assert len(result) > 0


def test_horse_list_view():
    from src.plugins.jx3.horse import v2
    mc = MessageCallback()
    v2.jx3_cmd_horseinfo_map = mc

    func = src.plugins.jx3.jx3_horseinfo
    event = SFGroupMessageEvent()

    mc.tag = '马场 唯满侠'
    event.message = obMessage(mc.tag)
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_horseinfo_map, event)

    task = func(event, args)
    ext.SyncRunner.as_sync_method(task)
    mc.check_counter()
