from .TeamUserType import *
# from src.plugins.jx3.user_attribute import *

class TeamUser:
    '''团队成员'''
    name: str
    remark: str
    role: TeamUserType
    attribute: UserAttribute
