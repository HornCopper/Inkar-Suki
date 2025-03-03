# DPS计算器 莫问

"""
build getDps.js
"""

from typing import Literal, Any
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
from src.plugins.jx3.attributes.mobile_attr import mobile_attribute_calculator
from src.templates import SimpleHTML, get_saohua

import httpx

from ._template import template_calculator, template_attr
from .base import BaseCalculator

class Talents(Qixue):
    @property
    def location(self) -> tuple[str, str, str] | None:
        for x in self.qixue_data[self.kungfu]:
            for y in self.qixue_data[self.kungfu][x]:
                if self.qixue_data[self.kungfu][x][y]["name"] == self.name:
                    return x, self.qixue_data[self.kungfu][x][y]["id"], "https://icon.jx3box.com/icon/" + str(self.qixue_data[self.kungfu][x][y]["icon"]) + ".png"

class Mowen(Kungfu):
    @classmethod
    def with_internel_id(cls, internel_id) -> "Self | str":
        if int(internel_id) not in [10447, 101124]:
            current_kungfu = super().with_internel_id(internel_id).name or "无法识别"
            return "该计算器与心法不符合，请检查后重试！\n当前识别的心法：" + current_kungfu
        return super().with_internel_id(internel_id)

class MowenCalculator(BaseCalculator):
    all_loop_talents: dict[str, list[str]] = {
        "橙武一段流照": ["飞帆", "明津", "连徽", "流照", "豪情", "师襄", "知止", "刻梦", "争鸣", "云汉", "参连", "正律和鸣"],
        "一段流照": ["飞帆", "明津", "连徽", "流照", "豪情", "师襄", "知止", "刻梦", "争鸣", "云汉", "参连", "正律和鸣"],
        "二段响壑": ["飞帆", "明津", "连徽", "流照", "豪情", "师襄", "知止", "刻梦", "争鸣", "云汉", "参连", "响壑"],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = EquipDataProcesser(self.data)

    @property
    def kungfu(self) -> Mowen:
        kungfu = Mowen.with_internel_id(
            self.data["data"]["Kungfu"]["KungfuID"]
        )
        if isinstance(kungfu, str):
            raise ValueError(kungfu)
        return kungfu
    
    @property
    def cw(self) -> bool:
        for each_equip in self.data["data"]["Equips"]:
            if each_equip["Name"] in ["抚今", "栖贤韵"]:
                return True
        return False
    
    @property
    def haste(self) -> int:
        return int(mobile_attribute_calculator(self.data["data"]["Equips"], "莫问")["加速"])
    
    @property
    def loop(self) -> str:
        _2_haste = False
        if self.haste >= 9232:
            _2_haste = True
        cw = self.cw
        if cw:
            return "橙武一段流照"
        else:
            if not _2_haste:
                return "一段流照"
            else:
                return "二段响壑"

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
        return result

    async def calculate(self):
        async with httpx.AsyncClient(verify=False) as client:
            url = "http://10.0.10.13:41412/calculate"
            params = {"loop": self.loop}
            json_ = self.data
            data: dict = (await client.post(url, params=params, json=json_, timeout=30)).json()
        return data
    
    async def image(self):
        data = await self.calculate()
        battle_time = data["time"]
        dps = data["dps"]
        loop_name = self.loop
        _loop_talents = self.all_loop_talents[loop_name]
        loop_talents = {}
        for t in _loop_talents:
            x, y, icon = (await Qixue.create({"name": t}, "莫问")).location or ("", "", "")
            loop_talents[t] = icon
        tables = []
        for skill_data in data["skills"]:
            tables.append(
                Template(template_calculator).render(
                    **{
                        "skill": str(skill_data["name"]),
                        "display": str(
                            round(
                                skill_data["damage"]
                                / data["skills"][0]["damage"]
                                * 100,
                                2,
                            )
                        )
                        + "%",
                        "percent": skill_data["percent"],
                        "count": str(skill_data["count"]),
                        "value": "{:,}".format(int(skill_data["damage"])),
                    }
                )
            )
        attributes = self.attr
        attrs = []
        for panel in attributes:
            attrs.append(
                Template(template_attr).render(
                    name=panel.name,
                    value=panel.value,
                    income="未知",
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
                    "dps": dps,
                    "desc": f"计算器来源：莫问在线配装计算器 By 一慕尔如星一<br>当前循环：{loop_name} / 战斗时长："
                    + str(battle_time)
                    + f"s<br>玩家：{name}·{server}",
                    "attrs": attrs,
                    "skills": tables,
                    "talents": {t.name: t.icon for t in (await self.parser.qixue())},
                    "loop_talents": loop_talents,
                    "saohua": get_saohua(),
                },
            )
        )
        image = await generate(html, ".container", False, segment=True)
        return image
