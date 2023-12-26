from ... import *

import src.plugins.jx3
from src.plugins.jx3 import wiki, get_guide


def test_question():
    mc = MessageCallback()
    wiki.jx3_cmd_wiki = mc

    func = src.plugins.jx3.jx3_wiki
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = '小药简介'  # 将返回含有图片的项
    task = func(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

    func = src.plugins.jx3.jx3_next_ques  # 转到相关问题
    mc.tag = 'xg0'  # 相关项
    task = func(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()

    mc.tag = 'yy0'  # 引用项
    task = func(state, event, obMessage(mc.tag))
    asyncio.run(task)
    mc.check_counter()


def test_noanswer():
    arg_keywords = '小药'
    task = get_guide(arg_keywords)
    result = asyncio.run(task)
    assert '尝试换个方式问问' in result.question.results[0]
