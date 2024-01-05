from __future__ import annotations
import enum


class IArgDesc:
    name: str
    description: str
    example: list[str]

    def __init__(self, name: str = None, description: str = None, example: list[str] = None) -> None:
        self.name = name
        self.description = description
        self.example = example

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'example': self.example,
        }


class Jx3ArgsType(enum.Enum):
    '''参数类型'''

    default = IArgDesc(example=['苹果', '书本', '火锅'])
    '''默认'''
    string = IArgDesc(example=['苹果', '书本', '火锅'])
    '''文本'''
    number = IArgDesc(example=[1, 2, 3])
    '''数值'''
    server = IArgDesc(example=['唯满侠', '双梦', '煎蛋'])
    '''区服'''
    pageIndex = IArgDesc(example=[1, 2, 3])
    '''页码'''
    pageSize = IArgDesc(example=[5, 10, 50, 100])
    '''每页条数'''
    kunfu = IArgDesc(example=['孤锋诀', '莫问', '山海经诀', '相知'])
    '''心法'''
    school = IArgDesc(example=['万宁', '药宗', '蓬莱'])
    '''门派'''
    property = IArgDesc(example=['五行石', '太一玄晶', '砂'])
    '''道具名称'''
    user = IArgDesc(example=['打本本', '锦鲤鲤', '步龄龄'])
    '''玩家id'''
    pvp_mode = IArgDesc(example=['22', '33', '55'])
    '''pvp模式'''
    subscribe = IArgDesc(example=['日常', '攻防', '新闻'])
    '''事件订阅'''
    command = IArgDesc(example=['交易行', '战绩', '物价'])
    '''命令'''

    def to_dict(self):
        return self.value.to_dict()


for t in Jx3ArgsType:
    if not isinstance(t.value, IArgDesc):
        continue
    t.value.name = t.name
    if not t.value.description:
        t.value.description = t.__doc__
