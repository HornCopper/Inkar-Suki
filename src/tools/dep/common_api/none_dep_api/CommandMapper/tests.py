from .CommandRunner import *


def test_command_mapper_common():
    mapper = {
        '早': '早早早',
        '你好-$1-小狗': '你好-小狗-$1',
        '你好-$1-大狗': '你好-大狗-$1',
        '你好-$pos-大猫': '你好-大大-$pos',
        '你好2-$po-大猫-$pos-2': '你好-大大-$pos-$po-3',
        '张2': '张3',
        '张1': '张2',
        '张0': '张1',
        '张x': '张y',
        '张y': '张x',
        '张x1': '张x2',
        '张x2': '张x',
    }
    assert CommandMapper(mapper).convert('早') == '早早早'
    assert CommandMapper(mapper).convert('早 北京') == '早早早 北京'
    assert CommandMapper(mapper).convert(['早', '北京']) == '早早早 北京'

    assert CommandMapper(mapper).convert('张1 北京') == '张3 北京'

    assert CommandMapper(mapper).convert('张x 北京') == '张y 北京'
    assert CommandMapper(mapper).convert('张x1 北京') == '张y 北京'

    assert CommandMapper(mapper).convert('你好 北京 小狗') == '你好 小狗 北京'
    assert CommandMapper(mapper).convert('你好 山东 大狗 1') == '你好 大狗 山东 1'


def test_jx3_command_mapper():
    mapper = {
        '属性': '属性v3',
        '配装-pve-$kunfu': '配装-$kunfu-pve',
    }
    assert CommandMapper(mapper).convert('属性 而遇') == '属性v3 而遇'
    assert CommandMapper(mapper).convert('配装 pve 丐帮') == '配装 丐帮 pve'
