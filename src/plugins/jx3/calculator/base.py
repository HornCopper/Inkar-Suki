from typing_extensions import Self

from src.const.prompts import PROMPT
from src.utils.database.player import search_player
from src.utils.database.attributes import AttributesRequest

from src.plugins.jx3.attributes.v2_remake import (
    EquipDataProcesser,
    Panel
)

class BaseCalculator:
    calculator_url = "http://10.0.10.26:11223"

    @classmethod
    async def with_name(cls, name: str, server: str, tag: str) -> "Self | str":
        player_data = (await search_player(role_name = name, server_name = server)).format_jx3api()
        if player_data["code"] != 200:
            return PROMPT.PlayerNotExist
        instance = await AttributesRequest.with_name(server, name)
        if not instance:
            return PROMPT.PlayerNotExist
        equip_data = instance.get_equip(tag)
        if not equip_data:
            return PROMPT.EquipNotFound
        return cls(equip_data, (name, server))
    
    def __init__(self, tuilan_data: dict, info: tuple[str, str]):
        self.data = tuilan_data
        self.info = info
        self.parser = EquipDataProcesser(self.data)

    @property
    def attr(self) -> list[Panel]:
        result = []
        for p in self.parser.panel:
            if p.name in [
                "面板攻击",
                "会心",
                "会心效果",
                "破防",
                "无双",
                "破招",
                "加速",
                "身法",
            ]:
                if p.name == "面板攻击":
                    p.name = "攻击"
                    result.append(p)
                else:
                    result.append(p)
        # min_wd, max_wd = self.weapon_damage
        # result.append(Panel(name="武器伤害", value=f"{min_wd} - {max_wd}"))
        return result
    
    @property
    def haste(self) -> str:
        for each_panel in self.attr:
            if each_panel.name == "加速":
                value = int(each_panel.value)
                if value < 206:
                    return "零段"
                elif 206 <= value < 9232:
                    return "一段"
                elif 9232 <= value < 19285:
                    return "二段"
                elif 19285 <= value < 30158:
                    return "三段"
                elif 30158 <= value < 42057:
                    return "四段"
                else:
                    return "五段"
        return "零段"