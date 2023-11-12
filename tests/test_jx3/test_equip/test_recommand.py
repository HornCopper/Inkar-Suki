from ... import *

from src.plugins.jx3 import equip_recommend


@pytest.mark.skipif(not Config.jx3_token, reason="无token时不测试")
def test_recommend_menu():
    mc = MessageCallback()
    equip_recommend.jx3_cmd_equip_recommend = mc

    func = equip_recommend.jx3_equip_recommend_menu
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = '刀宗'
    task = func(event, state, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

    return state


@pytest.mark.skipif(True, reason="当前配置文件页面无法访问到")
@pytest.mark.skipif(not Config.jx3_token, reason="无token时不测试")
def test_recommend():
    mc = MessageCallback()
    equip_recommend.jx3_cmd_equip_recommend = mc

    func = equip_recommend.equip_recmded
    state = test_recommend_menu()
    event = SFGroupMessageEvent()

    mc.tag = '0'
    task = func(event, state, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


def test_kunfu():
    assert aliases('策T') == '铁牢律'
    assert std_kunfu('策T')
    assert std_kunfu('策T').belong == '天策'


def test_school():
    assert kftosh('KFC') == '藏剑'
    assert kftoschool('衍天宗')
    assert kftoschool('衍天宗').name == '衍天'
