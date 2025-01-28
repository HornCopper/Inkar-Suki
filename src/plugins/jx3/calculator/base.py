from typing_extensions import Self

from src.const.prompts import PROMPT
from src.const.jx3.server import Server
from src.utils.database.player import search_player
from src.utils.network import Request

class BaseCalculator:
    @classmethod
    async def with_name(cls, name: str, server: str) -> "Self | str":
        player_data = (await search_player(role_name = name, server_name = server)).format_jx3api()
        if player_data["code"] != 200:
            return PROMPT.PlayerNotExist
        role_id = player_data["data"]["roleId"]
        params = {
            "game_role_id": role_id,
            "zone": Server(server).zone,
            "server": server
        }
        data = (await Request("https://m.pvp.xoyo.com/mine/equip/get-role-equip", params=params).post(tuilan=True)).json()
        return cls(data, (name, server))
    
    def __init__(self, tuilan_data: dict, info: tuple[str, str]):
        self.data = tuilan_data
        self.info = info