from .. import *


def test_auto_args_number():
    templates = [
        Jx3Arg(Jx3ArgsType.command),
        Jx3Arg(Jx3ArgsType.command, default=None, alias='新命令'),
        Jx3Arg(Jx3ArgsType.group_id, default=None, alias='群号'),
        Jx3Arg(Jx3ArgsType.bool, default=False, alias='是否全局'),
    ]
    event = SFGroupMessageEvent()
    event.group_id = 1211125  # 避免缓存

    args = argparser.get_args('原命令 [empty] 是', templates, event)
    pass
    assert args == ['原命令', None, None, True]


def test_invalid_arguments():
    templates = [
        Jx3Arg(Jx3ArgsType.server),
    ]
    event = SFGroupMessageEvent()
    event.group_id = 1211125  # 避免缓存
    args = argparser.get_args('哈哈哈', templates, event)
    assert type(args) is InvalidArgumentException
