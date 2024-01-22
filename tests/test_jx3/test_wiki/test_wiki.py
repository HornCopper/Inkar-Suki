from ... import *

import src.plugins.jx3
from src.plugins.jx3 import wiki, get_guide


def test_question():
    mc = MessageCallback()
    wiki.jx3_cmd_wiki = mc

    func1 = src.plugins.jx3.jx3_wiki
    state = {}
    event = SFGroupMessageEvent()

    mc.tag = '接引人 三山四海攻略'  # 将返回含有图片的项
    event.message = obMessage(mc.tag)
    args = Jx3Arg.arg_factory(src.plugins.jx3.jx3_cmd_wiki, event)
    task = func1(state, event, args)
    asyncio.run(task)
    mc.check_counter()

    func2 = src.plugins.jx3.jx3_next_ques  # 转到相关问题
    mc.tag = 'xg0'  # 相关项
    event.message = obMessage(mc.tag)
    task = func2(state, event, event.message)
    asyncio.run(task)
    mc.check_counter()

    mc.tag = 'yy0'  # 引用项
    event.message = obMessage(mc.tag)
    task = func2(state, event, event.message)
    asyncio.run(task)
    mc.check_counter()


def test_noanswer():
    # arg_keywords = '小药好看点的！本赛季的！' # 客服加进知识库了
    arg_keywords = '不要鸡大萌，好看点的！'
    task = get_guide(arg_keywords)
    result = asyncio.run(task)
    assert '尝试换个方式问问' in result.question.results[0][0]
