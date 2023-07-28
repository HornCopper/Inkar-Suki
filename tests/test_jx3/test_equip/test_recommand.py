from ... import *

from src.plugins.jx3 import equip_recommend

@pytest.mark.skipif(not Config.jx3_token, reason="无token时不测试")
def test_recommend_menu():
    mc = MessageCallback()
    equip_recommend.jx3_cmd_equip_recommend = mc

    func = equip_recommend.jx3_equip_recommend_menu
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = "刀宗"
    task = func(event, state, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()
