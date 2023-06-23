from .. import *


def test_args():
    templates = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(Jx3ArgsType.string)]
    driver.on_bot_connect
    args = get_args('唯满侠 测试', templates)
    assert args[0] == '唯我独尊'
    assert args[1] == '测试'

    args = get_args('测试', templates)
    assert args[0] == None
    assert args[1] == '测试'

    args = get_args('', templates)
    assert args[0] == None
    assert args[1] == None

    templates = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(
        Jx3ArgsType.string, is_optional=False), Jx3Arg(Jx3ArgsType.pageIndex)]
    args = get_args('唯满侠 测试', templates)
    assert args[0] == '唯我独尊'
    assert args[1] == '测试'
    assert args[2] == None

    args = get_args('唯满侠', templates)
    assert isinstance(args, Exception)
    
