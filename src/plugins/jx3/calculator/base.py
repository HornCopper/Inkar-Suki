from typing_extensions import Self

# from src.plugins.jx3.calculator.baj import BeiaojueCalculator
# from src.plugins.jx3.calculator.bxj import BingxinjueCalculator
# from src.plugins.jx3.calculator.dj import DujingCalculator
# from src.plugins.jx3.calculator.fsj import FenshanjinCalculator
# from src.plugins.jx3.calculator.fysj import FenyingshengjueCalculator
# from src.plugins.jx3.calculator.lhj import LinghaijueCalculator
# from src.plugins.jx3.calculator.mw import MowenCalculator
# from src.plugins.jx3.calculator.mzllt import MingzunliulitiCalculator
# from src.plugins.jx3.calculator.tgy import TieguyiCalculator
# from src.plugins.jx3.calculator.tll import TielaolvCalculator
# from src.plugins.jx3.calculator.txjy import TaixujianyiCalculator
# from src.plugins.jx3.calculator.wf import WufangCalculator
# from src.plugins.jx3.calculator.xsj import XisuijingCalculator
from src.config import Config
from src.const.prompts import PROMPT
from src.utils.database.player import search_player
from src.utils.database.attributes import AttributesRequest

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

from src.plugins.jx3.attributes.v2_remake import (
    EquipDataProcesser,
    Panel
)

# CalcTypes = {
#     10627: WufangCalculator,
#     10081: BingxinjueCalculator,
#     10015: TaixujianyiCalculator,
#     10062: TielaolvCalculator,
#     10243: MingzunliulitiCalculator,
#     10389: TieguyiCalculator,
#     10002: XisuijingCalculator,
#     10533: LinghaijueCalculator,
#     10447: MowenCalculator,
#     10390: FenshanjinCalculator,
#     10175: DujingCalculator,
#     10464: BeiaojueCalculator,
#     10242: FenyingshengjueCalculator
# }

class BaseCalculator:
    calculator_url = Config.jx3.api.calculator_url

    @classmethod
    async def with_name(cls, name: str, server: str, tag: str) -> "Self | str":
        player_data = await search_player(role_name = name, server_name = server)
        if player_data.roleId == "":
            return PROMPT.PlayerNotExist
        instance = await AttributesRequest.with_name(server, name)
        if not instance:
            return PROMPT.PlayerNotExist
        equip_data = instance.get_equip(tag)
        if isinstance(equip_data, bool):
            return PROMPT.PlayerNotExist if equip_data else PROMPT.EquipNotFound
        return cls(tuilan_data = equip_data, info = (name, server))
    
    def __init__(self, tuilan_data: dict = {}, info: tuple[str, str] = ("", "")):
        self.data = tuilan_data
        self.info = info
        self.parser = EquipDataProcesser(self.data)
        self.income_list = []
        self.income_ver = ""
        self.formation_list = []
        self.formation_name = ""

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