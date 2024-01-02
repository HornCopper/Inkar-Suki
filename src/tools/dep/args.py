
from enum import IntEnum


class Jx3ArgsType(IntEnum):
    '''任意'''
    default = 0
    '''文本'''
    string = 1
    '''数值'''
    number = 2
    '''区服'''
    server = 3
    '''页码'''
    pageIndex = 4
    '''每页条数'''
    pageSize = 5
    '''心法'''
    kunfu = 6
    '''门派'''
    school = 7
    '''道具名称'''
    property = 8
    '''玩家id'''
    user = 9
    '''pvp模式'''
    pvp_mode = 10

    
