from __future__ import annotations
from src.tools.dep.data_server import *
from src.tools.utils import *
from src.tools.dep.jx3.Jx3ApiResponse import *
from src.tools.config import Config
_bot = Config.bot
_token = Config.jx3api_globaltoken


class Jx3PlayerInfo:
    def __init__(self, data: dict = None) -> None:
        if data is None:
            return
        self.load_data(data)

    def load_data(self, data: dict):
        self.updateAt: float = data.get('updateAt') or DateTime().timestamp()
        '''数据更新时间'''
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
        self.forceName: str = data.get('forceName')
        '''门派'''
        self.forceId: str = data.get('forceId')
        '''门派id'''
        self.bodyName: str = data.get('bodyName')
        '''体态：成男 成女 萝莉 正态'''
        self.bodyId: str = data.get('bodyId')
        '''体态id'''
        self.tongName: str = data.get('tongName')
        '''?'''
        self.tongId: str = data.get('tongId')
        '''?'''
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
        return self.__dict__
