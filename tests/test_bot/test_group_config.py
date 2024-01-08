from .. import *


def test_group_config():
    config = GroupConfig(776484255)
    assert config.mgr_property('server') == '幽月轮'
    config.mgr_property('server', '唯我独尊')
    assert config.mgr_property('server') == '唯我独尊'
    config.mgr_property('server', '幽月轮')

    next_time = DateTime('2024-05-01').timestamp()
    start_time = DateTime('2023-01-01').timestamp()
    assert config.mgr_property('auth.start') == start_time
    assert config.mgr_property('auth.start', next_time) == start_time
    assert config.mgr_property('auth.start') == next_time
    assert config.mgr_property('auth.start', start_time) == next_time
