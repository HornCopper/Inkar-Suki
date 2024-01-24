
from ... import *


def test_horse_loader():
    import src.plugins.jx3.horse.v2
    result = asyncio.run(src.plugins.jx3.horse.v2.get_horse_reporter('唯我独尊'))
    assert len(result) > 0


def test_horse_list_data():
    from src.plugins.jx3.horse import v2

    func = src.plugins.jx3.get_jx3_horse_info
    event = SFGroupMessageEvent()

    event.message = obMessage('马场 唯满侠')
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_horseinfo_map, event)

    task = func(args)
    result = ext.SyncRunner.as_sync_method(task)
    assert len(result[1]) > 3, '马场不过滤时记录应该很多'

    horse_name = '赤兔'
    event.message = obMessage(f'马场 唯满侠 {horse_name}')
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_horseinfo_map, event)

    task = func(args)
    result = ext.SyncRunner.as_sync_method(task)
    assert all([horse_name in rec.get('horses') for rec in result[1]]), f'所有记录应该都是关于{horse_name}的'


def test_horse_list_view():
    from src.plugins.jx3.horse import v2
    mc = MessageCallback()
    v2.jx3_cmd_horseinfo_map = mc

    func = src.plugins.jx3.jx3_horseinfo
    event = SFGroupMessageEvent()

    mc.tag = '马场 唯满侠'
    event.message = obMessage(mc.tag)
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_horseinfo_map, event)

    task = func(args)
    ext.SyncRunner.as_sync_method(task)
    mc.check_counter()
