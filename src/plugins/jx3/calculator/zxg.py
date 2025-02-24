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
    Panel,
    EquipDataProcesser,
)
from src.templates import SimpleHTML, get_saohua

from ._template import template_calculator, template_attr
from .base import BaseCalculator

class Zixiagong(Kungfu):
    @classmethod
    def with_internel_id(cls, internel_id) -> "Self | str":
        if int(internel_id) not in [10014]:
            current_kungfu = super().with_internel_id(internel_id).name or "无法识别"
            return "该计算器与心法不符合，请检查后重试！\n当前识别的心法：" + current_kungfu
        return super().with_internel_id(internel_id)
    
class ZixiagongCalculator(BaseCalculator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = EquipDataProcesser(self.data)

    @property
    def kungfu(self) -> Zixiagong:
        kungfu = Zixiagong.with_internel_id(
            self.data["data"]["Kungfu"]["KungfuID"]
        )
        if isinstance(kungfu, str):
            raise ValueError(kungfu)
        return kungfu

    @property
    def haste(self) -> int:
        """
        加速
        """
        for each_attr in self.data["data"]["PersonalPanel"]:
            if each_attr["name"] == "加速":
                return int(each_attr["value"])
        raise ValueError("无法确定加速！")
    
    @property
    def talents(self) -> list[str]:
        talents_data = self.data["data"]["Person"]["qixueList"]
        return [t["name"] for t in talents_data]
    
    @property
    def cw(self) -> bool:
        for each_equip in self.data["data"]["Equips"]:
            if each_equip["Name"] in ["苍冥游", "仙灵"]:
                return True
        return False
    
    @property
    def mode(self) -> str:
        cw_flag = self.cw
        haste = self.haste
        if not cw_flag:
            return "紫武及格档"
        elif cw_flag and (206 <= haste < 9232):
            return "橙武一段加速标准模式"
        elif cw_flag and (9232 <= haste):
            return "橙武二段加速标准模式"
        return "紫武及格档"
    
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
        """
        特效腰坠
        """
        for each_equip in self.data["data"]["Equips"]:
            if each_equip["Name"] == "画青山":
                return "25900风特效"
        return "无"
    
    @property
    def effect_weapon(self) -> str:
        """
        特效武器
        """
        for each_equip in self.data["data"]["Equips"]:
            if each_equip["Name"] == "如云浮":
                return "25900水特效"
        return "无"
    
    @property
    def enchants(self) -> list[str]:
        """
        腰带、护腕、鞋大附魔
        """
        enchants = []
        location_map = {
            "腰带": "腰带",
            "护臂": "护腕",
            "鞋": "鞋子"
        }
        for location in ["腰带", "护臂", "鞋"]:
            for each_equip in self.data["data"]["Equips"]:
                if each_equip["Icon"]["SubKind"] == location:
                    if "WCommonEnchant" in each_equip:
                        enchants.append(
                            ("全等级" if location == "腰带" else each_equip["Quality"]) + \
                            location_map[location] + "大附魔"
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
        for a in ["基础攻击力", "攻击力", "会心", "会心效果", "破防", "无双", "破招"]:
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
    def spirit(self) -> int:
        """根骨"""
        for attr in (self.data["data"]["PersonalPanel"] or []):
            if attr["name"] == "根骨":
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
            "effect_weapon": self.effect_weapon,
            "is_school_effect": school_effect,
            "is_school_damage": school_damage,
            "special_effects": [],
            "talents": self.talents,
            "mode": self.mode
        }
        final_result = (await Request(
            "http://10.0.10.13:17171/calculator_zxg",
            params=params,
            headers={"token": Config.hidden.offcial_token}
        ).post(timeout=40)).json()
        return final_result
    
    def parse_attr(self, role_attr: list[Panel], income_data: list) -> list[str]:
        result = []
        attr_typs = ["基础攻击力", "根骨", "会心", "会心效果", "破防", "无双", "破招"]
        for each_attr in role_attr:
            if each_attr.name in attr_typs:
                result.append(
                    Template(template_attr).render(
                        name = each_attr.name,
                        value = each_attr.value,
                        income = round(float(income_data[attr_typs.index(each_attr.name)]), 3)
                    )
                )
        result = [Template(template_attr).render(name=role_attr[1].name, value=role_attr[1].value, income="未知")] + \
        result + \
        [Template(template_attr).render(name="根骨", value=str(self.spirit), income=round(float(income_data[1]), 3))]
        return result
    
    @staticmethod
    def _to_float(percent: str) -> float:
        return float(percent[:-1]) / 100
    
    @staticmethod
    def _to_percent(float_value: float) -> str:
        return str(round(float_value * 100, 2)) + "%"
    
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
                        "skill": skill_data["name"].replace("两仪", "两仪化形").replace("四象", "四象轮回").replace("六合", "六合独尊"),
                        "display": self._to_percent(
                            self._to_float(skill_data["percent"]) / self._to_float(skills_data[0]["percent"])
                        ),
                        "percent": skill_data["percent"],
                        "count": str(skill_data["count"]),
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
                    "desc": "计算器来源：【丝路风语】气纯DPS计算器 by 月慕青尘<br>延迟：<60ms / 战斗时长：300" + \
                        f"s<br>玩家：{name}·{server}",
                    "attrs": self.parse_attr(self.attr, data["data"]["income"]),
                    "skills": tables,
                    "talents": {t.name: t.icon for t in (await self.parser.qixue())},
                    "loop_talents": None,
                    "saohua": get_saohua(),
                },
            )
        )
        image = await generate(html, ".container", False, segment=True)
        return image