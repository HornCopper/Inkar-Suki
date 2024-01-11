from __future__ import annotations
from src.tools.dep.data_server import *
from src.tools.utils import *
from src.tools.dep.jx3.Jx3ApiResponse import *
from src.tools.config import Config
_bot = Config.bot
_token = Config.jx3api_globaltoken


class Jx3PlayerLoader:
    cache_uid = filebase_database.Database(
        f'{bot_path.common_data_full}player_role_id',
        serializer=lambda data: dict([[x, data[x].to_dict()] for x in data]),
        deserializer=lambda data: dict([[x, Jx3PlayerUid(data[x])] for x in data]),
    )
    cache_detail = filebase_database.Database(
        f'{bot_path.common_data_full}player_roles',
        serializer=lambda data: dict([[x, data[x].to_dict()] for x in data]),
        deserializer=lambda data: dict([[x, Jx3Player(data[x])] for x in data]),
    ).value

    async def get_user_uid(server: str, userid: str):
        key = f'{server}{}'
        prev = Jx3PlayerLoader.cache_uid.get(key)
        url = f"{Config.jx3api_link}/data/role/detailed?token={_token}&server={server}&name={userid}"
        data = await Jx3ApiRequest(url).output_data()
        return Jx3Player(data)


class Jx3PlayerUid:
    def __init__(self, data: dict = None) -> None:
        if data is None:
            return
        self.__data = data
        self.load_data(data)

    def load_data(self, data: dict):
        self.updateAt = data.get('updateAt') or DateTime().timestamp()
        '''数据更新时间'''
        self.uid = data.get('uid')
        '''区服大区'''

    def to_dict(self):
        return self.__dict__


class Jx3Player:
    def __init__(self, data: dict = None) -> None:
        if data is None:
            return
        self.__data = data
        self.load_data(data)

    def load_data(self, data: dict):
        self.updateAt = data.get('updateAt') or DateTime().timestamp()
        '''数据更新时间'''
        self.zoneName = data.get('zoneName')
        '''区服大区'''
        self.serverName = data.get('serverName')
        '''区服名'''
        self.roleName = data.get('roleName')
        '''角色名'''
        self.roleId = data.get('roleId')
        '''角色区内id'''
        self.globalRoleId = data.get('globalRoleId')
        '''角色id'''
        self.forceName = data.get('forceName')
        '''门派'''
        self.forceId = data.get('forceId')
        '''门派id'''
        self.bodyName = data.get('bodyName')
        '''体态：成男 成女 萝莉 正态'''
        self.bodyId = data.get('bodyId')
        '''体态id'''
        self.tongName = data.get('tongName')
        '''?'''
        self.tongId = data.get('tongId')
        '''?'''
        self.campName = data.get('campName')
        '''阵营：恶人谷 浩气盟 中立'''
        self.campId = data.get('campId')
        '''阵营id'''
        self.personName = data.get('personName')
        '''推栏名称'''
        self.personId = data.get('personId')
        '''账号id'''
        self.personAvatar = data.get('personAvatar')
        '''推栏头像'''

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_uid(cls, uid: str) -> Jx3Player:
        pass

    @classmethod
    def from_id(cls, server: str, user_id: str) -> Jx3Player:
        pass
