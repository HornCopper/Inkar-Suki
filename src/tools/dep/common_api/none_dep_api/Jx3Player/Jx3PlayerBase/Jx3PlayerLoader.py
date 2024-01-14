from __future__ import annotations
from .Jx3PlayerInfoUid import *
from .Jx3PlayerInfo import *
from src.tools.dep.common_api.none_dep_api.Jx3ApiResponse import *
_token = Config.jx3api_globaltoken


class Jx3PlayerLoader:
    cache_uid: dict[str, Jx3PlayerInfoUid] = filebase_database.Database(
        f'{bot_path.common_data_full}player_role_id',
        serializer=lambda data: dict([[x, data[x].to_dict()] for x in data]),
        deserializer=lambda data: dict([[x, Jx3PlayerInfoUid(data[x])] for x in data]),
    ).value
    cache_detail: dict[str, Jx3PlayerInfo] = filebase_database.Database(
        f'{bot_path.common_data_full}player_roles',
        serializer=lambda data: dict([[x, data[x].to_dict()] for x in data]),
        deserializer=lambda data: dict([[x, Jx3PlayerInfo(data[x])] for x in data]),
    ).value

    @staticmethod
    def get_user(server: str, userid: str, cache_length: float = 30*86400):
        key = f'{server}@{userid}'

        prev = Jx3PlayerLoader.cache_uid.get(key)
        if prev and (DateTime() - DateTime(prev.updateAt)).total_seconds() < cache_length:
            # 30天内直接使用缓存
            uid = prev.roleId
            return Jx3PlayerLoader.cache_detail[uid]
        return None

    @staticmethod
    async def get_user_async(server: str, userid: str, cache_length: float = 86400):
        if cache_length > 0:
            result = Jx3PlayerLoader.get_user(server, userid, cache_length)
            if result:
                return result

        key = f'{server}@{userid}'

        url = f"{Config.jx3api_link}/data/role/detailed?token={_token}&server={server}&name={userid}"
        data = await Jx3ApiRequest(url).output_data()
        role_info = Jx3PlayerInfo(data)
        role_id = Jx3PlayerInfoUid(data)

        Jx3PlayerLoader.cache_uid[key] = role_id
        Jx3PlayerLoader.cache_detail[role_id.roleId] = role_info
        return Jx3PlayerLoader.cache_detail[role_id.roleId]


class Jx3PlayerInfoWithInit(Jx3PlayerInfo):
    @classmethod
    def from_uid(cls, uid: str) -> Jx3PlayerInfo:
        result = Jx3PlayerLoader.cache_detail.get(uid)
        return result

    @classmethod
    def from_id(cls, server: str, user_id: str, cache_length: float = None) -> Jx3PlayerInfo:
        t = Jx3PlayerLoader.get_user_async(server, user_id, cache_length=cache_length)
        return ext.SyncRunner.as_sync_method(t)
