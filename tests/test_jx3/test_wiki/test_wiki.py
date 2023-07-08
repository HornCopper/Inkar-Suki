from ... import *

import src.plugins.jx3
from src.plugins.jx3 import wiki


def test_question():
    mc = MessageCallback()
    wiki.jx3_cmd_wiki = mc

    func = src.plugins.jx3.jx3_wiki
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = '端午节活动'
    task = func(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

    func = src.plugins.jx3.jx3_next_ques # 转到相关问题
    mc.tag = 'xg0'  # 相关项
    task = func(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

    mc.tag = 'yy0'  # 引用项
    task = func(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()
