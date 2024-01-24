from __future__ import annotations
from src.tools.utils import *
from src.tools.config import Config
from ...common import *
from src.constant.jx3 import *


class Jx3PlayerInfo(BaseUpdateAt):
    def __init__(self, data: dict = None) -> None:
        if data is None:
            return
        self.load_data(data)

    def load_data(self, data: dict):
        super().load_data(data)
        self.zoneName: str = data.get('zoneName')
        '''区服大区'''
        self.serverName: str = data.get('serverName')
        '''区服名'''
        self.roleName: str = data.get('roleName')
        '''角色名'''
        self.roleId: str = data.get('roleId')
        '''角色区内id'''
        self.globalRoleId: str = data.get('globalRoleId')
        '''角色id'''
        force_name = data.get('forceName') or 'unknown'
        school: School = School.from_alias(force_name)
        self.forceName: str = school and school.name
        '''门派'''
        self.forceId: str = data.get('forceId')
        '''门派id'''
        self.bodyName: str = data.get('bodyName')
        '''体态：成男 成女 萝莉 正态'''
        self.bodyId: str = data.get('bodyId')
        '''体态id'''
        self.tongName: str = data.get('tongName')
        '''帮会名称'''
        self.tongId: str = data.get('tongId')
        '''帮会id'''
        self.campName: str = data.get('campName')
        '''阵营：恶人谷 浩气盟 中立'''
        self.campId: str = data.get('campId')
        '''阵营id'''
        self.personName: str = data.get('personName')
        '''推栏名称'''
        self.personId: str = data.get('personId')
        '''账号id'''
        self.personAvatar: str = data.get('personAvatar')
        '''推栏头像'''

    def to_dict(self):
        result = copy.deepcopy(self.__dict__)
        return result
