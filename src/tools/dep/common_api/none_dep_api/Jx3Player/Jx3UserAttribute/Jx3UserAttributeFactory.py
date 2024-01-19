from __future__ import annotations
from .Jx3UserAttributeInfo import *
from ...common import *
from src.tools.dep.data_server import *
from src.tools.utils import *
from .IJx3UserAttributeFactory import *
from src.tools.dep.common_api.none_dep_api.tuilan import *
from src.tools.config import *


class Jx3UserAttributeFactory(IJx3UserAttributeFactory):
    def __init__(self, data: dict) -> None:
        self.__data = data
        self.data: BaseJx3UserAttribute = None  # 初始化
        self.load_data()

    @property
    def success(self):
        return self.__data and self.__data.get('code') == 0

    @property
    def raw_data(self):
        if not self.success:
            return None
        return self.__data.get('data')

    def load_data(self):
        raw_data = self.raw_data
        if not raw_data:
            return
        self.data = BaseJx3UserAttribute(raw_data)

    @staticmethod
    async def _get_attribute_by_uid(uid: str, server: str) -> BaseJx3UserAttribute:
        server: Server = Server.from_alias(server)
        param = {
            "zone": server.belong,
            "server": server.name,
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
        logger.debug(f'load user attributes from tuilan:{server.name}@{uid}')
        data = await post_url(url="https://m.pvp.xoyo.com/mine/equip/get-role-equip", data=payload, headers=headers)
        response = Jx3UserAttributeFactory(json.loads(data)).data
        if not response:
            logger.warning(f'fail load attribute [{server.name}@{uid}]:{data}')
        return response
