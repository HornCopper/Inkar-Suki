from ... import *
from src.tools.dep.data_server import *


def test_server_map():
    assert server_mapping('唯满侠') == '唯我独尊'
    assert server_mapping('双梦') == '梦江南'
    assert server_mapping('风骨霸刀') == '绝代天骄'
    assert server_mapping('飞龙在天') == '飞龙在天'
    assert server_mapping('念破') == '破阵子'
    pass


@pytest.mark.skipif(not Config.jx3api_link, reason="无jx3api_link时不测试")
def test_server_status():
    def default_cb_finish(msg: str):
        if '开服状态：' in msg:
            return
        assert False, mc.to_warning(f'fail run:{msg}')
    mc = MessageCallback(cb_finish=default_cb_finish)

    import src.plugins.jx3.server
    jx3_server = src.plugins.jx3.server.jx3_server
    src.plugins.jx3.server.cmd_jx3_server = mc
    event = SFGroupMessageEvent()

    mc.tag = '双梦'
    task = jx3_server(event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


def test_server_bind():
    event = SFGroupMessageEvent()
    from src.plugins.jx3.bind import server_bind
    server_bind(event.group_id, '唯满侠')
    x = server_mapping(None, group_id=event.group_id)
    assert x == '唯我独尊'
