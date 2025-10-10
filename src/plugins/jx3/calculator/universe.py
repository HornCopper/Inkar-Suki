# DPS计算器 铁牢律

from typing import Literal
from typing_extensions import Self
from jinja2 import Template

from src.const.jx3.kungfu import Kungfu
from src.const.path import ASSETS, build_path
from typing import overload
from src.utils.network import Request
from src.utils.generate import generate
from src.templates import SimpleHTML, get_saohua
from src.utils.database.attributes import JX3PlayerAttribute, Talent

from ._template import template_calculator_v2
from .base import BaseCalculator

class Universal(Kungfu):
    @classmethod
    def with_internel_id(cls, internel_id) -> "Self | str":
        # if int(internel_id) not in [10062, 100407]:
        #     current_kungfu = super().with_internel_id(internel_id).name or "无法识别"
        #     return "该计算器与心法不符合，请检查后重试！\n当前识别的心法：" + current_kungfu
        return super().with_internel_id(internel_id)

class UniversalCalculator(BaseCalculator):
    def __init__(self, jcl_data: list[list] = [], kungfu_id: int = 0, **kwargs):
        self.jcl_data = jcl_data
        self.kungfu_id = kungfu_id
        super().__init__(**kwargs)
    
    def attrs(self, attributes: dict[str, float]) -> dict[str, str]:
        attr_names = {
            "BaseAttack": "基础攻击",
            "FinalAttack": "最终攻击",
            "Surplus": "破招值",
            "Critical": "会心等级",
            "CriticalDamage": "会心效果等级",
            "Overcome": "破防等级",
            "Strain": "无双等级",
            "Haste": "加速等级",
            # "CriticalPercent": "会心（百分比）",
            # "CriticalDamagePercent": "会心效果（百分比）",
            # "OvercomePercent": "破防（百分比）",
            # "StrainPercent": "无双（百分比）",
            # "HastePercent": "加速（百分比）",
        }
        results = {}
        for each_attr_name in attr_names.keys():
            value = attributes[each_attr_name]
            if each_attr_name.endswith("Percent"):
                final_value = str(round(value * 100, 2)) + "%"
            else:
                final_value = str(int(value))
            results[attr_names[each_attr_name]] = final_value
        return results

    async def get_loop(self):
        url = f"{self.calculator_url}/loops?kungfu_id={self.kungfu_id or self.equip_data.kungfu_id}"
        data = (await Request(url).get()).json()
        results = {}
        if data["code"] == 404:
            return ""
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
            params["jcl_data"] = self.equip_data.equip_lines
            params["kungfu_id"] = self.equip_data.kungfu_id
            url_path = "calculator_raw"
        data = (await Request(f"{self.calculator_url}/{url_path}", params=params).post(timeout=30)).json()
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
            talent = Talent(t)
            _loop_talents[talent.name] = talent.icon
        loop_talents = _loop_talents
        tables = []
        for skill_data in data["damage_details"]:
            tables.append(
                Template(template_calculator_v2).render(
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
                        "critical": str(skill_data["critical"]),
                        "percent": str(round(skill_data["damage"] / data["total_damage"] * 100, 2)) + "%",
                        "count": str(skill_data["count"]),
                        "value": "{:,}".format(int(skill_data["damage"])),
                    }
                )
            )
        kungfu = Kungfu.with_internel_id(self.equip_data.kungfu_id)
        name, server = self.info
        html = str(
            SimpleHTML(
                html_type="jx3",
                html_template="calculator_new",
                **{
                    "font": build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"]),
                    "color": kungfu.color,
                    "kungfu": kungfu.name,
                    "icon": kungfu.icon,
                    "final_dps": str(int(data["damage_per_second"])),
                    "name": name,
                    "server": server,
                    "score": data["attributes"]["score"],
                    "loop": f"{data['weapon']}·{data['haste']}-{data['loop_name']}",
                    "provider": data['provider'],
                    "time": data['battle_time'],
                    "skills": "\n".join(tables),
                    "attrs": self.attrs(data["attributes"]),
                    "income": self.income_ver,
                    "formation": self.formation_name,
                    "loop_talents": loop_talents,
                    "saohua": get_saohua(),
                },
            )
        )
        image = await generate(html, ".container", False, segment=True, full_screen=True)
        return image