from ... import *

import src.plugins.jx3
from src.plugins.jx3 import wiki

def test_question():
    mc = MessageCallback()
    wiki.jx3_cmd_wiki = mc

    func = src.plugins.jx3.jx3_wiki
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = '五行石'
    task = func(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()
