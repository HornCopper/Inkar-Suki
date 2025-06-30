# DPS计算器 无方

from typing import Literal
from typing_extensions import Self
from jinja2 import Template

from src.const.jx3.kungfu import Kungfu
from src.const.path import ASSETS, build_path
from typing import overload
from src.utils.network import Request
from src.utils.generate import generate
from src.plugins.jx3.attributes.v2_remake import (
    Panel,
    Qixue,
    Talent,
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

class Taixujianyi(Kungfu):
    @classmethod
    def with_internel_id(cls, internel_id) -> "Self | str":
        if int(internel_id) not in [10015, 100389]:
            current_kungfu = super().with_internel_id(internel_id).name or "无法识别"
            return "该计算器与心法不符合，请检查后重试！\n当前识别的心法：" + current_kungfu
        return super().with_internel_id(internel_id)

class TaixujianyiCalculator(BaseCalculator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def kungfu(self) -> Taixujianyi:
        kungfu = Taixujianyi.with_internel_id(
            self.data["data"]["Kungfu"]["KungfuID"]
        )
        if isinstance(kungfu, str):
            raise ValueError(kungfu)
        return kungfu
    
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
    
    @property
    def raw_equips(self) -> list[dict]:
        """
        原始数据（排序后）
        """
        self.parser.equips
        sorted_equips = self.parser._cached_equips
        return sorted_equips or []
    
    @property
    def cw(self) -> bool:
        for each_equip in self.raw_equips:
            if each_equip["Name"] in ["镇恶", "风霆肃"]:
                return True
        return False

    @overload
    async def talents(self, with_icon: Literal[True]) -> list[Talent]: ...

    @overload
    async def talents(self, with_icon: Literal[False]) -> list[dict[str, int | str]]: ... # noqa: F811

    async def talents(self, with_icon: bool = False) -> list[dict[str, int | str]] | list[Talent]: # noqa: F811
        kungfu = self.kungfu.name
        if str(kungfu).endswith("·悟"):
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

    async def get_loop(self):
        url = f"{self.calculator_url}/loops?kungfu_id={self.kungfu.id}"
        data = (await Request(url).get()).json()
        results = {}
        for each_loop in data["data"]:
            name = each_loop["name"]
            weapon, haste_loop = name.split("·")
            haste, loop = haste_loop.split("_")
            results[name] = {"weapon": weapon, "haste": haste, "loop": loop}
        return results

    async def calculate(self, loop_arg: dict[str, str]):
        params = {
            "kungfu_id": self.kungfu.id,
            "tuilan_data": self.data,
            **loop_arg
        }
        data = (await Request(f"{self.calculator_url}/calculator", params=params).post()).json()
        if data["code"] == 404:
            return "加速不符合任何计算循环，请自行提供JCL或调整装备！"
        return data
    
    async def image(self, loop_arg: dict[str, str]):
        data = await self.calculate(loop_arg)
        if isinstance(data, str):
            return data
        _loop_talents = {}
        loop_talents = ["心固", "和光", "化三清", "无意", "玄门", "叠刃", "切玉", "负阴", "故长", "期声", "无欲", "风逝"]
        for t in loop_talents:
            x, y, icon = (await Qixue.create({"name": t}, "太虚剑意")).location or (
                "",
                "",
                "",
            )
            _loop_talents[t] = icon
        loop_talents = _loop_talents
        tables = []
        for skill_data in data["damage_details"]:
            tables.append(
                Template(template_calculator).render(
                    **{
                        "skill": str(skill_data["name"]),
                        "display": str(
                            round(
                                skill_data["damage"]
                                / data["damage_details"][0]["damage"]
                                * 100,
                                2,
                            )
                        )
                        + "%",
                        "percent": str(round(skill_data["damage"] / data["total_damage"] * 100, 2)) + "%",
                        "count": str(skill_data["count"]),
                        "value": "{:,}".format(int(skill_data["damage"])),
                    }
                )
            )
        attributes = self.attr
        attrs = []
        for panel in attributes:
            # for income_data in data["data"][flag]["attributeIncomeBoList"]:
                # if income_data["attributeName"] == panel.name:
                    attrs.append(
                        Template(template_attr).render(
                            name=panel.name,
                            value=panel.value,
                            # income=round(income_data["attributeIncome"], 3),
                            income="未知"
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
                    "dps": str(int(data["damage_per_second"])),
                    "desc": f"计算器JCL循环名称：{data['weapon']}·{data['haste']}-{data['loop_name']}\n<br>提供者：{data['provider']} / 战斗时长：{data['battle_time']}" \
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