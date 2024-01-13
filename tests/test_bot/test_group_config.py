from .. import *


def test_group_config():
    config = GroupConfig(776484255)
    config.mgr_property('server', '幽月轮')
    assert config.mgr_property('server') == '幽月轮'
    config.mgr_property('server', '唯我独尊')
    assert config.mgr_property('server') == '唯我独尊'
    config.mgr_property('server', '幽月轮')

    next_time = DateTime('2024-05-01').timestamp()
    start_time = DateTime('2024-01-08').timestamp()
    assert config.mgr_property('auth.start') == start_time
    assert config.mgr_property('auth.start', next_time) == start_time
    assert config.mgr_property('auth.start') == next_time
    assert config.mgr_property('auth.start', start_time) == next_time


def test_group_independence():
    config = GroupConfig(random.randint(int(1e7), int(1e8)))
    xxx = config.mgr_property('subscribe')
    xxx['test'] = '1'

    config2 = GroupConfig(random.randint(int(1e7), int(1e8)))
    xxx2 = config2.mgr_property('subscribe')
    assert xxx2.get('test') is None

    config._db.delete()
    config2._db.delete()

