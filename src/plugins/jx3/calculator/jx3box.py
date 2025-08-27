# 魔盒导入配装

# DPS计算器 铁牢律

from typing_extensions import Self
from jinja2 import Template

from src.const.jx3.kungfu import Kungfu
from src.const.path import ASSETS, build_path

from src.utils.network import Request
from src.utils.generate import generate
from src.plugins.jx3.attributes.v2_remake import (
    Qixue
)
from src.templates import SimpleHTML, get_saohua

from ._template import template_calculator
from .base import BaseCalculator

class Talents(Qixue):
    @property
    def location(self) -> tuple[str, str, str] | None:
        for x in self.qixue_data[self.kungfu]:
            for y in self.qixue_data[self.kungfu][x]:
                if self.qixue_data[self.kungfu][x][y]["name"] == self.name:
                    return x, self.qixue_data[self.kungfu][x][y]["id"], "https://icon.jx3box.com/icon/" + str(self.qixue_data[self.kungfu][x][y]["icon"]) + ".png"

class JX3BOX(Kungfu):
    @classmethod
    def with_internel_id(cls, internel_id) -> "Self | str":
        return super().with_internel_id(internel_id)

class JX3BOXCalculator(BaseCalculator):
    @classmethod
    async def with_pzid(cls, pzid: int):
        url = f"https://cms.jx3box.com/api/cms/app/pz/{pzid}"
        data = (await Request(url).get()).json()["data"]
        if data is None:
            return "未找到该配装方案，请检查后重试！"
        kungfu_id = data["mount"]
        equips: dict[str, dict] = data["content"]
        equips_lines = []
        locations = ["PRIMARY_WEAPON", None, "SECONDARY_WEAPON", "JACKET", "HAT", "NECKLACE", "RING_1", "RING_2", "BELT", "PENDANT", "BOTTOMS", "SHOES", "WRIST"]
        for location in locations:
            if location is None:
                continue
            index = locations.index(location)
            item_index = 6 if index in [0, 2] else (8 if index in [5, 6, 7, 9] else 7)
            equip_data = equips[location]
            item_id = equip_data["equip"]
            strength = equip_data["strength"]
            fivestones = [[5, int(each_fivestone) + 24441] for each_fivestone in equip_data["embedding"]]
            if equip_data["stone"] != "":
                fivestones.append([0, equip_data["stone"]])
            p_enchant = equip_data["enhance"] or 0
            c_enchant = equip_data["enchant"] or 0
            equips_lines.append(
                [
                    index,
                    item_index,
                    item_id,
                    strength,
                    fivestones,
                    p_enchant,
                    c_enchant,
                    0
                ]
            )
        return cls(jcl_data=equips_lines, kungfu_id=kungfu_id)

    def __init__(self, jcl_data: list[list] = [], kungfu_id: int = 0, *args, **kwargs):
        self.jcl_data = jcl_data
        self.kungfu_id = kungfu_id
        super().__init__(*args, **kwargs)

    @property
    def kungfu(self) -> Kungfu:
        kungfu = Kungfu.with_internel_id(self.kungfu_id)
        return kungfu

    async def get_loop(self):
        url = f"{self.calculator_url}/loops?kungfu_id={self.kungfu_id or self.kungfu.id}"
        data = (await Request(url).get()).json()
        results = {}
        if data["code"] != 200:
            return "该心法尚未实现计算器！"
        for each_loop in data["data"]:
            name = each_loop["name"]
            weapon, haste_loop = name.split("·")
            haste, loop = haste_loop.split("_")
            results[name] = {"weapon": weapon, "haste": haste, "loop": loop}
        return results

    async def calculate(self, loop_arg: dict[str, str]):
        params = {
            "full_income": self.income_list + self.formation_list,
            "kungfu_id": self.kungfu_id,
            # "tuilan_data": self.data,
            **loop_arg
        }
        if self.jcl_data:
            params["jcl_data"] = self.jcl_data
            url_path = "calculator_raw"
        else:
            params["tuilan_data"] = self.data
            params["kungfu_id"] = self.kungfu.id
            url_path = "calculator"
        data = (await Request(f"{self.calculator_url}/{url_path}", params=params).post()).json()
        if data["code"] == 404:
            return "加速不符合任何计算循环，请自行提供JCL或调整装备！"
        return data
    
    async def image(self, loop_arg: dict[str, str]):
        data = await self.calculate(loop_arg)
        if isinstance(data, str):
            return data
        _loop_talents = {}
        loop_talents = data["talents"]
        for t in loop_talents:
            x, y, icon = (await Qixue.create({"name": t}, str(self.kungfu.name))).location or (
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
                    + f"s",
                    "attrs": [],
                    "skills": tables,
                    "talents": {},
                    "loop_talents": loop_talents,
                    "saohua": get_saohua(),
                },
            )
        )
        image = await generate(html, ".container", False, segment=True)
        return image