from .. import *


def test_auto_args():
    ...  # TODO 测试各个参数的注入返回结果
    assert Jx3Arg(Jx3ArgsType.number).data('10')[0] == 10
    assert Jx3Arg(Jx3ArgsType.number).data('10')[1] == False

    assert Jx3Arg(Jx3ArgsType.number).data('你好')[0] == 0
    assert Jx3Arg(Jx3ArgsType.number).data('你好')[1] == True

    assert Jx3Arg(Jx3ArgsType.default).data('你好')[0] == '你好'
    assert Jx3Arg(Jx3ArgsType.default).data('你好')[1] == False

    assert Jx3Arg(Jx3ArgsType.bool).data('同意')[0] == True
    assert Jx3Arg(Jx3ArgsType.default).data('你好')[1] == False
