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
from src.templates import SimpleHTML

from ._template import msgbox_yinlongjue, template_calculator_yinlongjue

def generate_params(
    loop_name: str,
    loop_skill: List[str],
    attrs: dict,
    input_enchant: List[bool],
    set_list: List[str | None],
    special_equip: List[None | str]
) -> dict:
    enchant: List[int | str] = [12206, 12205, 12202, 12204, 12203]
    for num in range(5):
        if not input_enchant[num]:
            enchant[num] = ""
    params = {
        "playerReqDto": 
        {
            "attributeReqDto": attrs,
            "extraPointList": loop_skill,
            "recipeList": 
            [
                4996,
                4997,
                4985,
                4986,
                4987,
                4988,
                5004,
                5005,
                5006,
                5001,
                5002,
                5065,
                5069,
                5070,
                5071,
                5010,
                5011,
                5019,
                5050,
                5051
            ],
            "setList": set_list,
            "equipmentList": special_equip,
            "enchant2List": enchant,
            "position": "",
            "pzEquipmentReqDtoList": [],
            "stone": None,
            "isWuJie": False
        },
        "enemyReqDto": 
        {
            "sectName": "muZhuang124",
            "deBuffReqDtoList": 
            [
                {
                    "code": "chengLongJian",
                    "enable": False,
                    "num": 1,
                    "coverage": 0.33
                },
                {
                    "code": "longYin",
                    "enable": False,
                    "num": 1,
                    "coverage": 1
                },
                {
                    "code": "qiuSu",
                    "enable": False,
                    "num": 1,
                    "coverage": 1
                },
                {
                    "code": "xuRuo",
                    "enable": False,
                    "num": 1,
                    "coverage": 1
                }
            ]
        },
        "loopReqDto": 
        {
            "computeStrategy": "commonComputeStrategyImpl",
            "loopCode": loop_name
        }
    }
    return params

async def get_loop(loop_name: Literal["橙武遗恨", "猴王遗恨", "遗恨保百节", "猴王特效", "猴王"] = "遗恨保百节") -> Tuple[str | None, None | List[str]]:
    kw = {
        "橙武遗恨": "lxgCWYiHenLoop",
        "猴王遗恨": "lxgQiWangYiHenLoop",
        "遗恨保百节": "lxgBaoBaiJieYiHenLoop",
        "猴王特效": "lxgQiWangHouWangLoop",
        "猴王循环": "lxgHouWangLoop"
    }[loop_name]
    data = (await Request("http://www.j3lxg.cn/j3dps/api/public/v1/compute/getLoop").get()).json()
    for loop in data["data"]:
        if loop["code"] == kw:
            return kw, loop["extraPointList"]
    return None, None

async def get_tuilan_raw_data(server: str, uid: str) -> dict:
    params = {
        "zone": Server(server).zone,
        "server": server,
        "game_role_id": uid
    }
    equip_data = (await Request("https://m.pvp.xoyo.com/mine/equip/get-role-equip", params=params).post(tuilan=True)).json()
    return equip_data

class JX3Attributes:
    map: Dict[str, Tuple[Callable, str]] = {
        "基础攻击力": (lambda percent: percent, "jcgj"),
        "会心": (lambda percent: percent/100*78622.5, "jchx"),
        "会心效果": (lambda percent: (percent-175)/100*27513.75, "jchxxg"),
        "破防": (lambda percent: percent/100*78622.5, "jcpf"),
        "无双": (lambda percent: percent/100*75809.25, "jcws"),
        "破招": (lambda percent: percent, "jcpz"),
        "身法": (lambda percent: percent, "jcsf")
    }
    def __init__(self, data: dict):
        self.data: dict = data

    @property
    def weapon_damage(self) -> Tuple[int, int]:
        equips: list = self.data["data"]["Equips"]
        for equip in equips:
            if equip["Icon"]["Kind"] == "武器" and equip["Icon"]["SubKind"] != "投掷囊":
                base_damage = equip[f"Base1Type"]["Base1Min"]
                delta_damage = equip[f"Base2Type"]["Base2Min"]
                return int(base_damage), int(base_damage) + int(delta_damage)
        raise ValueError("Cannot find weapon!")


    @property
    def panel(self) -> dict:
        panel: list = self.data["data"]["PersonalPanel"]
        min_weapon, max_weapon = self.weapon_damage
        new_dict = {
            "jcld": 41,
            "wqshMin": int(min_weapon),
            "wqshMax": int(max_weapon)
        }
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
        equip_map = {
            "天地间": "39855",
            "变星霜": "38791",
            "雁无意": "37720",
            "空野": "37247",
            "山河同渡": "38072",
            "煞·山河同渡": "38072",
            "天峰里": "35776",
            "影壁孤": "34761",
            "鬓间黄泉": "37099"
        }
        for equip in equip_list:
            if equip["Name"] in ["天地间", "变星霜", "雁无意", "空野", "煞·山河同渡", "天峰里", "影壁孤"] or (equip["Name"] == "山河同渡" and equip["Quality"] == "12500") or (equip["Name"] == "鬓间黄泉" and equip["Quality"] == "11650"):
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

                    if effect["Desc"] == "atSkillEventHandler" and equipped_set_pieces >= set_num:
                        skill_event_handler_activated = True

                    if effect["Desc"] == "atSetEquipmentRecipe" and equipped_set_pieces >= set_num:
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
        
async def generate_calculator_img_yinlongjue(server: str, name: str):
    role_data = await search_player(role_name=name, server_name=server)
    role = role_data.format_jx3api()
    if role["code"] != 200:
        return [PROMPT.PlayerNotExist]
    data = await get_tuilan_raw_data(server, role["data"]["roleId"])
    kf_name = Kungfu.with_internel_id(data["data"]["Kungfu"]["KungfuID"])
    if kf_name != "隐龙诀":
        return False
    instance = JX3Attributes(data)
    loop_name, loop_skill = await get_loop()
    if not isinstance(loop_name, str) or not isinstance(loop_skill, list):
        return False
    params = generate_params(
        loop_name=loop_name,
        loop_skill=loop_skill,
        attrs=instance.panel,
        input_enchant=instance.enchant,
        set_list=instance.effect,
        special_equip=instance.special
    )
    data = (await Request("http://121.41.84.37/j3dps/api/public/v1/compute/dps", params=params).post()).json()
    tables = []
    for skill_data in data["data"]["mergeSkillDpsBoList"]:
        tables.append(
            Template(template_calculator_yinlongjue).render(**{
                "skill": skill_data["skillType"].replace("dot", "(DOT)"),
                "display": str(round(skill_data["proportion"]/data["data"]["mergeSkillDpsBoList"][0]["proportion"]*100, 2)) + "%",
                "percent": str(round(skill_data["proportion"], 2)) + "%",
                "count": str(skill_data["num"]),
                "value": str(int(skill_data["damage"]))
            })
        )
    html = str(SimpleHTML(
        html_type = "jx3",
        html_template = "calculator",
        **{
            "font": build_path(ASSETS, ["font", "custom.ttf"]),
            "yozai": build_path(ASSETS, ["font", "Yozai-Medium.ttf"]),
            "msgbox": Template(msgbox_yinlongjue).render(**{
                "dps": str(int(data["data"]["dps"]))
            }),
            "tables": "\n".join(tables),
            "school": "隐龙诀",
            "color": Kungfu("隐龙诀").color,
            "server": server,
            "name": name,
            "calculator": "【雾海寻龙】凌雪阁DPS计算器 by @猜猜<br>当前循环：遗恨保百节"
    }))
    final_path = await generate(html, ".total", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()