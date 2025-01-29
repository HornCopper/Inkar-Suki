# DPS计算器 紫霞功

from typing_extensions import Self
from jinja2 import Template

from src.config import Config
from src.const.jx3.kungfu import Kungfu
from src.const.path import ASSETS, build_path
from src.utils.analyze import sort_dict_list
from src.utils.network import Request
from src.utils.generate import generate
from src.plugins.jx3.attributes.v2_remake import (
    Qixue,
    Panel,
    EquipDataProcesser,
)
from src.templates import SimpleHTML, get_saohua

from ._template import template_calculator, template_attr
from .base import BaseCalculator

bx_talents = ["青梅嗅", "千里冰封", "新妆", "芳姿畅音", "枕上", "生莲", "流玉", "钗燕", "盈袖", "化冰", "明空", "凝华"]

class Bingxinjue(Kungfu):
    @classmethod
    def with_internel_id(cls, internel_id) -> "Self | str":
        if int(internel_id) not in [10081]:
            current_kungfu = super().with_internel_id(internel_id).name or "无法识别"
            return "该计算器与心法不符合，请检查后重试！\n当前识别的心法：" + current_kungfu
        return super().with_internel_id(internel_id)
    
class BingxinjueCalculator(BaseCalculator):
    cw_flag: bool | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = EquipDataProcesser(self.data)

    @property
    def kungfu(self) -> Bingxinjue:
        kungfu = Bingxinjue.with_internel_id(
            self.data["data"]["Kungfu"]["KungfuID"]
        )
        if isinstance(kungfu, str):
            raise ValueError(kungfu)
        return kungfu
    
    @property
    def weapon(self) -> str:
        for each_equip in self.data["data"]["Equips"]:
            if each_equip["Name"] == "淬血霜花剑·金莲":
                return "飞剑"
            if each_equip["Name"] == "飞霜绛露":
                self.cw_flag = True
                return "飞霜绛露"
            if each_equip["Name"] == "龙鲤":
                self.cw_flag = True
                return "龙鲤"
            if each_equip["Name"] == "月初生":
                return "水特效"
        return "无"
    
    @property
    def cw(self) -> bool:
        if isinstance(self.cw_flag, bool):
            return self.cw_flag
        flag = False
        for each_equip in self.data["data"]["Equips"]:
            if each_equip["Name"] in ["龙鲤", "飞霜绛露"]:
                flag = True
        return flag
    
    @property
    def set_effect(self) -> tuple[bool, bool]: # buff / 技能增伤
        for each_equip in self.data["data"]["Equips"]:
            if each_equip.get("BelongSchool", "") == self.kungfu.school and "ColorStone" not in each_equip and "SetListMap" in each_equip:
                school_set = each_equip["SetListMap"]
                if len(school_set) < 2:
                    return (False, False)
                elif 2 <= len(school_set) < 4:
                    return (True, False)
                elif 4 <= len(school_set):
                    return (True, True)
                else:
                    return (False, False)
        return (False, False)
    
    @property
    def effect_sash(self) -> str:
        for each_equip in self.data["data"]["Equips"]:
            if each_equip["Name"] == "画青山":
                return "画青山"
        return "无"
    
    @property
    def enchants(self) -> list[str]:
        """
        腰带、护腕、鞋大附魔
        """
        enchants = []
        location_map = {
            "腰带": "腰",
            "护臂": "腕",
            "鞋": "鞋"
        }
        for location in ["腰带", "护臂", "鞋"]:
            for each_equip in self.data["data"]["Equips"]:
                if each_equip["Icon"]["SubKind"] == location:
                    if "WCommonEnchant" in each_equip:
                        enchants.append(
                            ("小" if int(each_equip["Quality"]) <= 23500 else "大") + "伤" + location_map[location]
                        )
                    else:
                        enchants.append(
                            "无"
                        )
        return enchants
    
    @property
    def attr(self) -> list[Panel]:
        results = []
        personal_panel = self.data["data"]["PersonalPanel"] or []
        for a in ["根骨", "基础攻击力", "会心", "会心效果", "加速", "破防", "无双", "破招"]:
            for each_attr in personal_panel:
                if each_attr["name"] == a:
                    results.append(
                        Panel(
                            name = a,
                            value = (str(each_attr["value"]) if not each_attr["percent"] else str(each_attr["value"]) + "%")
                        )
                    )
        return results

    @property
    def attack(self) -> int:
        """攻击力"""
        for attr in (self.data["data"]["PersonalPanel"] or []):
            if attr["name"] == "攻击力":
                return int(attr["value"])
        return 0

    async def calculate(self) -> dict:
        attrs = self.attr
        detailed_attrs = {
            a.name: a.value
            for a in attrs
        }
        school_effect, school_damage = self.set_effect
        params = {
            "attributes": detailed_attrs,
            "enchants": self.enchants,
            "is_precious_weapon": self.cw,
            "effect_sash": self.effect_sash,
            "effect_weapon": self.weapon,
            "is_school_effect": school_effect,
            "is_school_damage": school_damage,
            "special_effects": [],
            "talents": []
        }
        final_result = (await Request(
            "http://10.0.10.13:17171/calculator_bxj",
            params=params,
            headers={"token": Config.hidden.offcial_token}
        ).post()).json()
        return final_result
    
    @staticmethod
    def _to_float(percent: str) -> float:
        return float(percent[:-1]) / 100
    
    @staticmethod
    def _to_percent(float_value: float) -> str:
        return str(round(float_value * 100, 2)) + "%"
    
    @staticmethod
    async def loop_talent() -> dict[str, str]:
        _loop_talents = {}
        for t in bx_talents:
            x, y, icon = (await Qixue.create({"name": t}, "冰心诀")).location or (
                "",
                "",
                "",
            )
            _loop_talents[t] = icon
        loop_talents = _loop_talents
        return loop_talents
    
    def parse_attr(self, role_panel: list[Panel], income_data: dict[str, str]):
        results = []
        for panel in role_panel:
            attr_name = panel.name
            if attr_name == "会心效果":
                attr_name = "会效"
            if attr_name == "基础攻击力":
                attr_name = "攻击"
            if attr_name in income_data.keys():
                results.append(
                    Template(template_attr).render(
                        name = panel.name,
                        value = panel.value,
                        income = income_data[attr_name]
                    )
                )
        results = [Template(template_attr).render(name="攻击力", value=str(self.attack), income="未知")] + results
        return results

    async def image(self):
        data = await self.calculate()
        if data["code"] != 200:
            return "计算失败！请联系机器人作者！"
        name, server = self.info
        tables = []
        skills_data = sort_dict_list(data["data"]["skills"], "damage")[::-1]
        for skill_data in skills_data:
            tables.append(
                Template(template_calculator).render(
                    **{
                        "skill": skill_data["name"],
                        "display": self._to_percent(
                            self._to_float(skill_data["percent"]) / self._to_float(skills_data[0]["percent"])
                        ),
                        "percent": skill_data["percent"],
                        "count": "N/A",
                        "value": "{:,}".format(int(skill_data["damage"])),
                    }
                )
            )
        html = str(
            SimpleHTML(
                html_type="jx3",
                html_template="calculator",
                **{
                    "font": build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"]),
                    "color": self.kungfu.color,
                    "kungfu": self.kungfu.name,
                    "dps": str(int(data["data"]["dps"])),
                    "desc": "计算器来源：【丝路风语】冰心DPS计算器 by 诺诺诺<br>延迟：30-60ms / 战斗时长：300" + \
                        f"s<br>玩家：{name}·{server}",
                    "attrs": self.parse_attr(self.attr, data["data"]["income"]),
                    "skills": tables,
                    "talents": {t.name: t.icon for t in (await self.parser.qixue())},
                    "loop_talents": await self.loop_talent(),
                    "saohua": get_saohua(),
                },
            )
        )
        image = await generate(html, ".container", False, segment=True)
        return image