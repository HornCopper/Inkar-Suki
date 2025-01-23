# DPS计算器 隐龙诀

"""
！！！！警告！！！！

务必获得凌雪阁计算器作者同意后再使用！！！！！
"""

from typing import Tuple, Literal, List, Dict, Callable
from jinja2 import Template
from pathlib import Path

from src.const.jx3.server import Server
from src.const.jx3.kungfu import Kungfu
from src.const.prompts import PROMPT
from src.const.path import ASSETS, build_path
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.database.player import search_player
from src.plugins.jx3.attributes.v2_remake import (
    Talent,
    Qixue,
    Panel,
    EquipDataProcesser,
)
from src.templates import SimpleHTML, get_saohua

from ._template import template_calculator, template_attr


def generate_params(
    loop_name: str,
    loop_skill: List[str],
    attrs: dict,
    input_enchant: List[bool],
    set_list: List[str | None],
    special_equip: List[None | str],
    pvx_attr: int = 0,
    sect_code: Literal["lxg", "lxgW"] = "lxg",
) -> dict:
    enchant: List[int | str] = [12206, 12205, 12202, 12204, 12203]
    for num in range(5):
        if not input_enchant[num]:
            enchant[num] = ""
    attrs["atPVXAllRound"] = pvx_attr
    params = {
        "playerReqDto": {
            "sectCode": sect_code,
            "attributeReqDto": attrs,
            "extraPointList": loop_skill,
            "recipeList": [
                4985,
                4986,
                4987,
                4988,
                4996,
                4997,
                5001,
                5002,
                5004,
                5005,
                5006,
                5065,
                5069,
                5070,
                5071,
                5010,
                5011,
                5019,
                5050,
                5051,
            ],
            "setList": set_list,
            "equipmentList": special_equip,
            "enchant2List": enchant,
            "position": "",
            "pzEquipmentReqDtoList": [],
            "stone": None,
            "isWuJie": False,
        },
        "enemyReqDto": {
            "sectName": "muZhuang134",
            "deBuffReqDtoList": [
                {"code": "chengLongJian", "enable": False, "num": 1, "coverage": 0.33},
                {"code": "longYin", "enable": False, "num": 1, "coverage": 1},
                {"code": "qiuSu", "enable": False, "num": 1, "coverage": 1},
                {"code": "xuRuo", "enable": False, "num": 1, "coverage": 1},
            ],
        },
        "loopReqDto": {
            "computeStrategy": "commonComputeStrategyImpl",
            "loopCode": loop_name,
        },
    }
    return params


async def get_loop(
    loop_name: Literal["橙武遗恨", "遗恨", "麒王切", "麒王循环"] = "遗恨",
    sect_code: Literal["lxg", "lxgW"] = "lxg",
) -> Tuple[str | None, None | List[str], list[str] | None]:
    kw = {
        "橙武遗恨": "lxgBaoBaiJieYiHenCWLoop",
        "遗恨": "lxgBaoBaiJieYiHenLoop",
        "麒王切": "lxgBeiqueSingleQiWangLoop",
        "麒王循环": "lxgBeiqueQiWangLoop",
    }[loop_name]
    data = (
        await Request(
            "http://www.j3lxg.cn/j3dps/api/public/v1/compute/getLoopBySectCode",
            params={"sectCode": sect_code},
        ).get()
    ).json()
    for loop in data["data"]:
        if loop["code"] == kw:
            return kw, loop["extraPointList"], loop["name"].split(":")[-1].split("/")
    return None, None, None


async def get_tuilan_raw_data(server: str, uid: str) -> dict:
    params = {"zone": Server(server).zone, "server": server, "game_role_id": uid}
    equip_data = (
        await Request(
            "https://m.pvp.xoyo.com/mine/equip/get-role-equip", params=params
        ).post(tuilan=True)
    ).json()
    return equip_data


class JX3Attributes:
    map: Dict[str, Tuple[Callable, str]] = {
        "基础攻击力": (lambda percent: percent, "jcgj"),
        "会心": (lambda percent: percent / 100 * 197703.0, "jchx"),
        "会心效果": (lambda percent: (percent - 175) / 100 * 72844.2, "jchxxg"),
        "破防": (lambda percent: percent / 100 * 225957.6, "jcpf"),
        "无双": (lambda percent: percent / 100 * 133333.2, "jcws"),
        "破招": (lambda percent: percent, "jcpz"),
        "身法": (lambda percent: percent, "jcsf"),
        "加速": (lambda percent: percent, "atHasteBase"),
    }

    def __init__(self, data: dict):
        self.data: dict = data
        self.parser = EquipDataProcesser(data)

    @property
    def weapon_damage(self) -> Tuple[int, int]:
        equips: list = self.data["data"]["Equips"]
        for equip in equips:
            if equip["Icon"]["Kind"] == "武器" and equip["Icon"]["SubKind"] != "投掷囊":
                base_damage = equip["Base1Type"]["Base1Min"]
                delta_damage = equip["Base2Type"]["Base2Min"]
                return int(base_damage), int(base_damage) + int(delta_damage)
        raise ValueError("Cannot find weapon!")

    @property
    def _pvxallround(self) -> int:
        attr = {}
        for each_equip in self.data["data"]["Equips"]:
            if "FiveStone" in each_equip:
                for each_fivestone in each_equip["FiveStone"]:
                    attr_name = each_fivestone["Desc"]
                    attr_value = int(each_fivestone["IncreaseGeneratedMagic"])
                    attr[attr_name] = attr.get(attr_name, 0) + attr_value
            if "effectColorStone" in each_equip:
                for each_attr in each_equip["effectColorStone"]["Attributes"]:
                    attr_name = each_attr["Desc"]
                    attr_value = float(each_attr["Attribute1Value1"])
                    attr[attr_name] = attr.get(attr_name, 0) + attr_value
        return attr.get("atPVXAllRound", 0)

    @property
    def panel(self) -> dict:
        panel: list = self.data["data"]["PersonalPanel"]
        min_weapon, max_weapon = self.weapon_damage
        new_dict = {"jcld": 41, "wqshMin": int(min_weapon), "wqshMax": int(max_weapon)}
        for attr in panel:
            if attr["name"] in list(self.map):
                func, key = self.map[attr["name"]]
                value = func(attr["value"])
                new_dict[key] = value
        return new_dict

    @property
    def special(self) -> list:
        equip_list: list = self.data["data"]["Equips"]
        result = []
        equip_map = {"连天际": "lianTianJi", "怨王侯": "yuanWangHou"}
        for special_equip in equip_map:
            for equip in equip_list:
                if equip["Name"] == special_equip:
                    result.append(equip_map[equip["Name"]])
        return result

    @property
    def effect(self) -> List[None | str]:
        equip_list: list = self.data["data"]["Equips"]
        skill_event_handler_activated = False
        set_equipment_recipe_activated = False

        for equip in equip_list:
            if "SetListMap" in equip and "Set" in equip:
                equipped_set_pieces = len(equip["SetListMap"])

                for effect in equip["Set"]:
                    set_num = int(effect.get("SetNum", 0))

                    if (
                        effect["Desc"] == "atSkillEventHandler"
                        and equipped_set_pieces >= set_num
                    ):
                        skill_event_handler_activated = True

                    if (
                        effect["Desc"] == "atSetEquipmentRecipe"
                        and equipped_set_pieces >= set_num
                    ):
                        set_equipment_recipe_activated = True

        if skill_event_handler_activated and set_equipment_recipe_activated:
            return ["5037", "5038", "1927"]
        if set_equipment_recipe_activated:
            return ["5037", "5038"]
        if skill_event_handler_activated:
            return ["1927"]
        return []

    @property
    def enchant(self) -> list:
        enchant_ = []
        for place in ["帽子", "上衣", "腰带", "护臂", "鞋"]:
            flag = False
            for equip in self.data["data"]["Equips"]:
                if equip["Icon"]["SubKind"] == place:
                    if "WPermanentEnchant" in equip:
                        enchant_.append(True)
                        flag = True
                    else:
                        enchant_.append(False)
                        flag = True
            if not flag:
                enchant_.append(False)
        return enchant_

    @property
    def kungfu(self) -> Kungfu:
        return Kungfu.with_internel_id(self.data["data"]["Kungfu"]["KungfuID"])

    async def qixue(self) -> list[Talent]:
        return await self.parser.qixue()

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
    def cw(self) -> bool:
        equips = [e["Name"] for e in self.data["data"]["Equips"]]
        if "山河同渡" in equips:
            return True
        if "长安" in equips:
            return True
        return False


async def generate_calculator_img_yinlongjue(server: str, name: str):
    role_data = await search_player(role_name=name, server_name=server)
    role = role_data.format_jx3api()
    if role["code"] != 200:
        return PROMPT.PlayerNotExist
    data = await get_tuilan_raw_data(server, role["data"]["roleId"])
    kf_name = Kungfu.with_internel_id(data["data"]["Kungfu"]["KungfuID"]).name
    if kf_name != "隐龙诀":
        return "不支持该心法！请检查命令和计算器是否一致！"
    instance = JX3Attributes(data)
    loop = "遗恨" if not instance.cw else "橙武遗恨"
    loop_name, loop_skill, loop_talent = await get_loop(loop)
    if (
        not isinstance(loop_name, str)
        or not isinstance(loop_skill, list)
        or not isinstance(loop_talent, list)
    ):
        return "不支持该计算器循环！请检查命令和计算器是否一致！"
    loop_talents = {}
    for t in loop_talent:
        if t == "望断":
            t = "忘断"
        x, y, icon = (await Qixue.create({"name": t}, "隐龙诀")).location or (
            "",
            "",
            "",
        )
        loop_talents[t] = icon
    params = generate_params(
        loop_name=loop_name,
        loop_skill=loop_skill,
        attrs=instance.panel,
        input_enchant=instance.enchant,
        set_list=instance.effect,
        special_equip=instance.special,
        pvx_attr=instance._pvxallround,
    )
    data = (
        await Request(
            "http://121.41.84.37/j3dps/api/public/v1/compute/dps", params=params
        ).post()
    ).json()
    tables = []
    for skill_data in data["data"]["mergeSkillDpsBoList"]:
        tables.append(
            Template(template_calculator).render(
                **{
                    "skill": skill_data["skillType"].replace("dot", "(DOT)"),
                    "display": str(
                        round(
                            skill_data["proportion"]
                            / data["data"]["mergeSkillDpsBoList"][0]["proportion"]
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
    attributes = instance.attr
    attrs = []
    for panel in attributes:
        for income_data in data["data"]["attributeIncomeBoList"]:
            if income_data["attributeName"] == panel.name:
                attrs.append(
                    Template(template_attr).render(
                        name=panel.name,
                        value=panel.value,
                        income=round(income_data["attributeIncome"], 3),
                    )
                )
    html = str(
        SimpleHTML(
            html_type="jx3",
            html_template="calculator",
            **{
                "font": build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"]),
                "color": instance.kungfu.color,
                "kungfu": instance.kungfu.name,
                "dps": str(int(data["data"]["dps"])),
                "desc": f"计算器来源：【丝路风语】凌雪阁DPS计算器 by @猜猜<br>当前循环：{loop} / 战斗时长："
                + str(data["data"]["totalTime"])
                + f"s<br>玩家：{name}·{server}",
                "attrs": attrs,
                "skills": tables,
                "talents": {t.name: t.icon for t in (await instance.qixue())},
                "loop_talents": loop_talents,
                "saohua": get_saohua(),
            },
        )
    )
    image = await generate(html, ".container", False, segment=True)
    return image
