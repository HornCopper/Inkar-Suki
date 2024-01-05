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

    '''文本'''
    default = IArgDesc(example=['苹果', '书本', '火锅'])
    string = IArgDesc(example=['苹果', '书本', '火锅'])
    '''数值'''
    number = IArgDesc(example=[1, 2, 3])
    '''区服'''
    server = IArgDesc(example=['唯满侠', '双梦', '煎蛋'])
    '''页码'''
    pageIndex = IArgDesc(example=[1, 2, 3])
    '''每页条数'''
    pageSize = IArgDesc(example=[5, 10, 50, 100])
    '''心法'''
    kunfu = IArgDesc(example=['孤锋诀', '莫问', '山海经诀', '相知'])
    '''门派'''
    school = IArgDesc(example=['万宁', '药宗', '蓬莱'])
    '''道具名称'''
    property = IArgDesc(example=['五行石', '太一玄晶', '砂'])
    '''玩家id'''
    user = IArgDesc(example=['打本本', '锦鲤鲤', '步龄龄'])
    '''pvp模式'''
    pvp_mode = IArgDesc(example=['22', '33', '55'])
    '''事件订阅'''
    subscribe = IArgDesc(example=['日常', '攻防', '新闻'])
    '''命令'''
    command = IArgDesc(example=['交易行', '战绩', '物价'])

    def to_dict(self):
        return self.value.to_dict()


for t in Jx3ArgsType:
    if not isinstance(t.value, IArgDesc):
        continue
    t.value.name = t.name
    if not t.value.description:
        t.value.description = t.__doc__
