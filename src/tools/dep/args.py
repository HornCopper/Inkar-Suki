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

    default = IArgDesc(example=['苹果', '书本', '火锅'], description='默认')
    '''默认'''
    string = IArgDesc(example=['苹果', '书本', '火锅'], description='文本')
    '''文本'''
    number = IArgDesc(example=[1, 2, 3], description='数值')
    '''数值'''
    bool = IArgDesc(example=[0, 1], description='真假')
    '''真假'''
    server = IArgDesc(example=['唯满侠', '双梦', '煎蛋'], description='区服')
    '''区服'''
    pageIndex = IArgDesc(example=[1, 2, 3], description='页码')
    '''页码'''
    pageSize = IArgDesc(example=[5, 10, 50, 100], description='每页条数')
    '''每页条数'''
    kunfu = IArgDesc(example=['孤锋诀', '莫问', '山海经诀', '相知'], description='心法')
    '''心法'''
    school = IArgDesc(example=['万宁', '药宗', '蓬莱'], description='门派')
    '''门派'''
    property = IArgDesc(example=['五行石', '太一玄晶', '砂'], description='道具名称')
    '''道具名称'''
    user = IArgDesc(example=['打本本', '锦鲤鲤', '步龄龄'], description='玩家id')
    '''玩家id'''
    pvp_mode = IArgDesc(example=['22', '33', '55'], description='pvp模式')
    '''pvp模式'''
    subscribe = IArgDesc(example=['日常', '攻防', '新闻'], description='事件订阅')
    '''事件订阅'''
    command = IArgDesc(example=['交易行', '战绩', '物价'], description='命令')
    '''命令'''
    url = IArgDesc(example=['baidu.com', 'http://xx.com', 'https://qq.com'], description='链接')
    '''链接'''

    def to_dict(self):
        return self.value.to_dict()


for t in Jx3ArgsType:
    if not isinstance(t.value, IArgDesc):
        continue
    t.value.name = t.name
