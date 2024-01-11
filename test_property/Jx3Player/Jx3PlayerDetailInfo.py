from __future__ import annotations
from src.tools.dep.data_server import *
from src.tools.utils import *
from src.tools.dep.jx3.Jx3ApiResponse import *
from src.tools.config import Config



class Jx3PlayerDetailInfo:
    def __init__(self) -> None:
        pass

    @staticmethod
    async def get_property_by_uid(uid: str, server: str) -> Jx3PlayerDetailInfo:
        param = {
            "zone": Zone_mapping(server),
            "server": server,
            "game_role_id": uid,
            "ts": gen_ts()
        }
        payload = format_body(param)
        xsk = gen_xsk(payload)
        headers = {
            "Host": "m.pvp.xoyo.com",
            "Accept": "application/json",
            "Accept-Language": "zh-cn",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "cache-control": "no-cache",
            "fromsys": "APP",
            "clientkey": "1",
            "apiversion": "3",
            "gamename": "jx3",
            "platform": "ios",
            "sign": "true",
            "token": ticket,
            "deviceid": device_id,
            "User-Agent": "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
            "x-sk": xsk
        }
        data = await post_url(url="https://m.pvp.xoyo.com/mine/equip/get-role-equip", data=payload, headers=headers)
        return data
