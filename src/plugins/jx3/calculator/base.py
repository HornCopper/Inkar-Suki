from typing import cast
from typing_extensions import Self

from src.config import Config
from src.const.prompts import PROMPT
from src.utils.database.player import search_player
from src.utils.database.attributes import JX3PlayerAttribute
from src.utils.database.classes import PlayerEquipsCache

INCOMES = {
    "无增益": [],
    "满增益": ["LDCF","CY","JF","HLSJ_1","HLSJ_2","PJ","XR","HXQJ","ZF","JHZ","CSY_SYMX","QS","LZWH","ZXYZ","XWGD","ZZM","PH","XQ","HRL"],
    "满增益风雷": ["LDCF","CY","JF","HLSJ_1","HLSJ_2","PJ","XR","HXQJ","ZF","JHZ","CSY_SYMX","QS","LZWH","ZXYZ","XWGD","NM","PH","XQ","HRL"]
}

FORMATIONS = {
    "无阵眼": [],
    "龙皇雪风阵": ["LHXFZ", "LHXFZ_5", "LHXFZ_SELF"],
    "千机百变阵": ["QJBBZ", "QJBBZ_PHYSICS"],
    "苍梧引灵阵": ["CWYLZ"],
    "九宫八卦阵": ["JGBGZ"],
    "万籁金弦阵": ["WLJXZ", "WLJXZ_SELF"],
    "墟海引归阵": ["XHYGZ", "XHYGZ_SELF"],
    "北斗七星阵": ["BDQXZ"],
    "七绝逍遥阵": ["QJXYZ"],
    "天鼓雷音阵": ["TGLYZ"],
    "万蛊噬心阵": ["WGSXZ", "WGSXZ_SELF"],
    "横云破锋阵": ["HYPFZ", "HYPFZ_SELF"]
}

class BaseCalculator:
    calculator_url = Config.jx3.api.calculator_url

    @classmethod
    async def with_global_role_id(cls, global_role_id: int, tag: str) -> "Self | str":
        instance = await JX3PlayerAttribute.from_database(global_role_id, tag, False)
        if instance is None:
            return PROMPT.EquipNotFound
        return cls(equip_data=instance, info=("未知", "未知"))

    @classmethod
    async def with_name(cls, name: str, server: str, tag: str) -> "Self | str":
        player_data = await search_player(role_name = name, server_name = server)
        if player_data.roleId == "":
            return PROMPT.PlayerNotExist
        await JX3PlayerAttribute.from_tuilan(player_data.roleId, player_data.serverName, player_data.globalRoleId)
        instance = await JX3PlayerAttribute.from_database(int(player_data.globalRoleId), tag, False)
        if instance is None:
            return PROMPT.EquipNotFound
        return cls(equip_data=instance, info=(name, server))
    
    def __init__(self, equip_data: JX3PlayerAttribute | None = None, info: tuple[str, str] = ("", "")):
        self.equip_data = cast(JX3PlayerAttribute, equip_data)
        self.info = info
        self.income_list = []
        self.income_ver = ""
        self.formation_list = []
        self.formation_name = ""