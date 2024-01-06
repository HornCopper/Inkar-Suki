from .. import *


def test_args():
    templates = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(Jx3ArgsType.string)]
    driver.on_bot_connect
    event = SFGroupMessageEvent()

    args = get_args('唯满侠 测试', templates, event)
    assert args[0] == '唯我独尊'
    assert args[1] == '测试'

    args = get_args('测试', templates, event)
    assert args[0] is None
    assert args[1] == '测试'

    args = get_args('', templates, event)
    assert args[0] is None
    assert args[1] is None

    templates = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(
        Jx3ArgsType.string, is_optional=False), Jx3Arg(Jx3ArgsType.pageIndex)]
    args = get_args('唯满侠 测试', templates)
    assert args[0] == '唯我独尊'
    assert args[1] == '测试'
    assert args[2] is None

    args = get_args('唯满侠', templates, event)
    assert isinstance(args, Exception)
