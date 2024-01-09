from .. import *


def test_auto_args_number():
    ...  # TODO 测试各个参数的注入返回结果
    assert Jx3Arg(Jx3ArgsType.number).data('10')[0] == 10
    assert Jx3Arg(Jx3ArgsType.number).data('10')[1] == False

    assert Jx3Arg(Jx3ArgsType.number).data(' 10')[0] == 10
    assert Jx3Arg(Jx3ArgsType.number).data(' 10')[1] == False

    assert Jx3Arg(Jx3ArgsType.number).data(' 10 ')[0] == 10
    assert Jx3Arg(Jx3ArgsType.number).data(' 10 ')[1] == False

    assert Jx3Arg(Jx3ArgsType.number).data('你好')[0] == 0
    assert Jx3Arg(Jx3ArgsType.number).data('你好')[1] == True

    assert Jx3Arg(Jx3ArgsType.default).data('你好')[0] == '你好'
    assert Jx3Arg(Jx3ArgsType.default).data('你好')[1] == False

    assert Jx3Arg(Jx3ArgsType.bool).data('同意')[0] == True
    assert Jx3Arg(Jx3ArgsType.default).data('你好')[1] == False


def test_auto_args_server_and_str_args():
    templates = [Jx3Arg(Jx3ArgsType.server), Jx3Arg(Jx3ArgsType.string)]
    driver.on_bot_connect
    event = SFGroupMessageEvent()
    event.group_id = 1211125 # 避免缓存

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
    assert args[2] == 0 # 默认返回第0页

    args = get_args('唯满侠', templates, event)
    assert isinstance(args, Exception)
