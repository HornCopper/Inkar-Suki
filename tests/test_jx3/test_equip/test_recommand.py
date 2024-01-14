from ... import *

from src.plugins.jx3 import equip_recommend
import src.plugins.jx3


def recommend_menu_check():
    mc = MessageCallback()
    equip_recommend.jx3_cmd_equip_recommend = mc

    func = equip_recommend.jx3_equip_recommend_menu
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = '配装 刀宗'
    event.message = obMessage(mc.tag)
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_equip_recommend, event)
    task = func(event, state, args)
    asyncio.run(task)
    mc.check_counter()
    return state


@pytest.mark.skipif('get_tuilan_articles' not in dir(), reason='无api可用')
def test_recommend_menu():
    recommend_menu_check()


@pytest.mark.skipif('get_tuilan_articles' not in dir(), reason='无api可用')
@pytest.mark.skipif(not Config.jx3_token, reason="无token时不测试")
def test_recommend():
    mc = MessageCallback()
    equip_recommend.jx3_cmd_equip_recommend = mc

    func = equip_recommend.equip_recmded
    state = recommend_menu_check()
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
    assert kftosh('莫问') == '长歌'
    assert kftosh('长歌') == '长歌'
    assert kftoschool('衍天宗')
    assert kftoschool('衍天宗').name == '衍天'
