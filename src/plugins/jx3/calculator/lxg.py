# DPS计算器 隐龙诀

"""
！！！！警告！！！！

务必获得凌雪阁计算器作者同意后再使用！！！！！
"""

from typing import Literal, Union, Any
from typing_extensions import Self
from jinja2 import Template

from src.const.jx3.kungfu import Kungfu
from src.const.path import ASSETS, build_path
from src.utils.typing import overload
from src.utils.network import Request
from src.utils.generate import generate
from src.plugins.jx3.attributes.v2_remake import (
    Panel,
    Qixue,
    Talent,
    EquipDataProcesser,
)
from src.templates import SimpleHTML, get_saohua

from ._template import template_calculator, template_attr
from .base import BaseCalculator

class Talents(Qixue):
    @property
    def location(self) -> tuple[str, str, str] | None:
        for x in self.qixue_data[self.kungfu]:
            for y in self.qixue_data[self.kungfu][x]:
                if self.qixue_data[self.kungfu][x][y]["name"] == self.name:
                    return x, self.qixue_data[self.kungfu][x][y]["id"], "https://icon.jx3box.com/icon/" + str(self.qixue_data[self.kungfu][x][y]["icon"]) + ".png"

class Lingxue(Kungfu):
    @classmethod
    def with_internel_id(cls, internel_id) -> "Self | str":
        if int(internel_id) not in [10585, 101173]:
            current_kungfu = super().with_internel_id(internel_id).name or "无法识别"
            return "该计算器与心法不符合，请检查后重试！\n当前识别的心法：" + current_kungfu
        return super().with_internel_id(internel_id)

    @property
    def sect_code(self):
        if str(self.name).endswith("·悟"):
            return "lxgW"
        else:
            return "lxg"

class LingxueCalculator(BaseCalculator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = EquipDataProcesser(self.data)

    @property
    def kungfu(self) -> Lingxue:
        kungfu = Lingxue.with_internel_id(
            self.data["data"]["Kungfu"]["KungfuID"]
        )
        if isinstance(kungfu, str):
            raise ValueError(kungfu)
        return kungfu
    
    @property
    def raw_equips(self) -> list[dict]:
        """
        原始数据（排序后）
        """
        self.parser.equips
        sorted_equips = self.parser._cached_equips
        return sorted_equips or []
        
    @property
    def equips(self) -> dict[str, dict[str, Any]]:
        """
        按魔盒格式化后的装备
        """
        raw_equips = self.raw_equips
        equip_locations = [
            "HAT",
            "JACKET",
            "BELT",
            "WRIST",
            "BOTTOMS",
            "SHOES",
            "NECKLACE",
            "PENDANT",
            "RING_1",
            "RING_2",
            "SECONDARY_WEAPON",
            "PRIMARY_WEAPON"
        ]
        equips = {}
        for equip in equip_locations:
            each_equip = raw_equips[equip_locations.index(equip)]
            if "WPermanentEnchant" in each_equip: # 小附魔
                enhance = int(each_equip["WPermanentEnchant"]["ID"])
            else:
                enhance = ""
            if "WCommonEnchant" in each_equip:
                enchant = int(each_equip["WCommonEnchant"]["ID"])
            else:
                enchant = ""
            if "ColorStone" in each_equip:
                color_stone = int(each_equip["ColorStone"]["ID"])
            else:
                color_stone = ""
            equips[equip] = {
                "id": each_equip["ID"],
                "stone": color_stone,
                "enchant": enchant,
                "enhance": enhance,
                "strength": int(each_equip["StrengthLevel"]),
                "embedding": [
                    int(fivestone["Level"])
                    for fivestone
                    in each_equip["FiveStone"]
                ] if "RING" not in equip else []
            }
        return equips
    
    @property
    def cw(self) -> bool:
        for each_equip in self.raw_equips:
            if each_equip["Name"] in ["长安", "山河同渡"]:
                return True
        return False

    @property
    def weapon_damage(self) -> tuple[int, int]:
        equips: list = self.data["data"]["Equips"]
        for equip in equips:
            if equip["Icon"]["Kind"] == "武器" and equip["Icon"]["SubKind"] != "投掷囊":
                base_damage = equip["Base1Type"]["Base1Min"]
                delta_damage = equip["Base2Type"]["Base2Min"]
                return int(base_damage), int(base_damage) + int(delta_damage)
        raise ValueError("Cannot find weapon!")
    
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
        min_wd, max_wd = self.weapon_damage
        result.append(Panel(name="武器伤害", value=f"{min_wd} - {max_wd}"))
        return result
    
    @overload
    async def talents(self, with_icon: Literal[True]) -> list[Talent]: ...

    @overload
    async def talents(self, with_icon: Literal[False]) -> list[dict[str, int | str]]: ... # noqa: F811

    async def talents(self, with_icon: bool = False) -> Union[list[dict[str, int | str]], list[Talent]]: # noqa: F811
        kungfu = self.kungfu.name
        if kungfu == "隐龙诀·悟":
            return []
        qixue_list = self.data["data"]["Person"]["qixueList"]
        if not with_icon:
            talents = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
        else:
            unknown_img = build_path(ASSETS, ["image", "jx3", "attributes", "unknown.png"])
            name = ["未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知"]
            icon = [unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img]
        kungfu = self.kungfu.name
        if kungfu is None:
            return []
        if qixue_list == []:
            return []
        for single_qixue in qixue_list:
            location = (await Qixue.create(single_qixue, kungfu)).location
            if location is None:
                continue
            x, id, _icon = location
            if not with_icon:
                talents[int(x)-1] = {"id": int(id), "name": single_qixue["name"]}
            else:
                name[int(x)-1] = single_qixue["name"]
                icon[int(x)-1] = _icon
        return talents \
            if not with_icon \
            else [
                Talent(icon=each_icon, name=each_name)
                for each_name, each_icon
                in zip(name, icon)
            ]
        
    async def loop(self) -> str:
        url = f"http://www.j3lxg.cn/j3dps/api/public/v1/compute/getLoopBySectCode?sectCode={self.kungfu.sect_code}"
        data = (await Request(url).get()).json()
        required_loop = "遗恨"
        if self.cw:
            required_loop = "橙武" + required_loop
        for each_loop in data["data"]:
            if str(each_loop["name"]).startswith(required_loop):
                return each_loop["code"]
        raise ValueError("无法找到对应循环！")
    
    async def calculate(self):
        params = {
            "loopCode": await self.loop(),
            "playerData": {
                "sectCode": self.kungfu.sect_code,
                "EquipList": self.equips,
                "TalentCode": await self.talents(False)
            }
        }
        data = (await Request("http://www.j3lxg.cn/j3dps/api/public/v1/compute/robot/dps", params=params).post()).json()
        return data
    
    async def image(self, full_income: bool = False):
        data = await self.calculate()
        flag = "allIncomeData" if full_income else "noIncomeData"
        loop_name, loop_talents = str(data["data"]["loopName"]).split(":")
        _loop_talents = {}
        for t in loop_talents.split("/"):
            if t == "望断":
                t = "忘断"
            x, y, icon = (await Qixue.create({"name": t}, "隐龙诀")).location or (
                "",
                "",
                "",
            )
            _loop_talents[t] = icon
        loop_talents = _loop_talents
        tables = []
        for skill_data in data["data"][flag]["mergeSkillDpsBoList"]:
            tables.append(
                Template(template_calculator).render(
                    **{
                        "skill": str(skill_data["skillType"]).replace("dot", "(DOT)").replace("-", "·"),
                        "display": str(
                            round(
                                skill_data["proportion"]
                                / data["data"][flag]["mergeSkillDpsBoList"][0]["proportion"]
                                * 100,
                                2,
                            )
                        )
                        + "%",
                        "percent": str(round(skill_data["proportion"], 2)) + "%",
                        "count": str(skill_data["num"]),
                        "value": "{:,}".format(int(skill_data["damage"])),
                    }
                )
            )
        attributes = self.attr
        attrs = []
        for panel in attributes:
            for income_data in data["data"][flag]["attributeIncomeBoList"]:
                if income_data["attributeName"] == panel.name:
                    attrs.append(
                        Template(template_attr).render(
                            name=panel.name,
                            value=panel.value,
                            income=round(income_data["attributeIncome"], 3),
                        )
                    )
        name, server = self.info
        html = str(
            SimpleHTML(
                html_type="jx3",
                html_template="calculator",
                **{
                    "font": build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"]),
                    "color": self.kungfu.color,
                    "kungfu": self.kungfu.name,
                    "dps": str(int(data["data"][flag]["dps"])),
                    "desc": f"计算器来源：【丝路风语】凌雪阁DPS计算器 by @猜猜<br>当前循环：{loop_name} / 战斗时长："
                    + str(data["data"][flag]["totalTime"])
                    + f"s<br>玩家：{name}·{server}",
                    "attrs": attrs,
                    "skills": tables,
                    "talents": {t.name: t.icon for t in (await self.talents(with_icon=True))},
                    "loop_talents": loop_talents,
                    "saohua": get_saohua(),
                },
            )
        )
        image = await generate(html, ".container", False, segment=True)
        return image
