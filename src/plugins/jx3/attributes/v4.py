from pathlib import Path
from jinja2 import Template

from src.const.prompts import PROMPT
from src.const.jx3.kungfu import Kungfu
from src.const.path import (
    ASSETS,
    TEMPLATES,
    build_path
)
from src.utils.file import read
from src.utils.database.player import search_player
from src.utils.database.attributes import AttributesRequest, AttributeParser
from src.utils.generate import generate
from src.plugins.jx3.attributes.v2_remake import Qixue, EquipDataProcesser
from src.plugins.jx3.trade.shilian import basic_name
from src.templates import get_saohua

import json

from .mobile_attr import mobile_attribute_calculator
from ._template import (
    template_enchant,
    template_equip,
    template_talent,
    template_other
)

class Equip:
    def __init__(self, equip_data: dict):
        self.equip_data = equip_data

    @staticmethod
    def _parse_attributes(data: dict) -> str:
        msg = ""
        for i in data["ModifyType"]:
            content = i["Attrib"]["GeneratedMagic"].split("提高")
            if len(content) == 1:
                content = content[0].split("增加")
            attr = content[0]
            attr = attr.replace("外功防御", "外防")
            attr = attr.replace("内功防御", "内防")
            attr = attr.replace("会心效果", "会效")
            filter_string = ["全", "阴性", "阳性", "阴阳", "毒性", "值", "成效", "内功", "外功", "体质", "等级", "混元性", "招式产生威胁", "水下呼吸时间", "抗摔系数", "马术气力上限", "气力上限"]
            for y in filter_string:
                attr = attr.replace(y, "")
            if attr != "" and len(attr) <= 4:
                msg = msg + f" {attr}"
        msg = msg.replace(" 能 ", " 全能 ").replace(" 能", " 全能")
        return msg.strip()

    @property
    def name(self) -> str:
        return self.equip_data["Name"]
    
    @property
    def icon(self) -> str:
        return self.equip_data["Icon"]["FileName"]
    
    @property
    def attr(self) -> str:
        return self._parse_attributes(self.equip_data)

    @property
    def color(self) -> str:
        return ["(167, 167, 167)", "(255, 255, 255)", "(0, 210, 75)", "(0, 126, 255)", "(254, 45, 254)", "(255, 165, 0)"][int(self.equip_data["Color"])]
    
    @property
    def effect(self) -> str:
        if str(self.equip_data["Name"]).startswith(basic_name):
            for each_attr in self.equip_data["ModifyType"]:
                if each_attr["Desc"] == "atSkillEventHandler":
                    return "，".join(str(each_attr["Attrib"]["Desc"])[:-1].split("。")[:-1]) + "。"
        return ""
    
    @property
    def quality(self) -> str:
        return self.equip_data["Quality"]
    
    @property
    def source(self) -> str:
        try:
            source = self.equip_data["equipBelongs"][0]["source"]
            source = source.split("；")[0]
        except (TypeError, IndexError, ValueError):
            source = ""
        return source
    
    @property
    def strength(self) -> str:
        return "⭐️" * int(self.equip_data["StrengthLevel"])
    
    @property
    def full_strengthen(self) -> bool:
        return (self.equip_data["StrengthLevel"] == self.equip_data["MaxStrengthLevel"])
    
    @property
    def enchants(self) -> list[str]:
        enchants = []
        if "WPermanentEnchant" in self.equip_data: # 小附魔
            enchants.append(
                Template(
                    template_enchant
                ).render(
                    icon = Path(ASSETS + "/image/jx3/attributes/permanent_enchant.png").as_uri(),
                    name = self.equip_data["WPermanentEnchant"]["Name"]
                )
            )
        if "WCommonEnchant" in self.equip_data: # 大附魔
            attrs_ = json.dumps(self.equip_data["ModifyType"], ensure_ascii=False)
            if attrs_.find("攻击") != -1:
                type_ = "伤"
            elif attrs_.find("治疗") != -1:
                type_ = "疗"
            else:
                type_ = "御"
            with open(
                build_path(
                    ASSETS,
                    [
                        "source",
                        "jx3",
                        "enchant_mapping.json"
                    ]
                ),
                encoding = "utf8",
                mode = "r"
            ) as f:
                enchant_data: dict = json.loads(f.read())
                for enchant_name in enchant_data:
                    if enchant_data[enchant_name]["min"] <= int(self.quality) <= enchant_data[enchant_name]["max"]:
                        enchants.append(
                            Template(
                                template_enchant
                            ).render(
                                icon = Path(ASSETS + "/image/jx3/attributes/common_enchant.png").as_uri(),
                                name = f"{enchant_name}·{type_}·" + {"帽子": "帽","上衣": "衣","腰带": "腰","护臂": "腕","鞋": "鞋"}[self.equip_data["Icon"]["SubKind"]]
                            )
                        )
        if "ColorStone" in self.equip_data: # 五彩石
            enchants.append(
                Template(
                    template_enchant
                ).render(
                    icon = self.equip_data["effectColorStone"]["Icon"]["FileName"],
                    name = self.equip_data["effectColorStone"]["Name"]
                )
            )
        return enchants
    
    @property
    def fivestones(self) -> dict[str, str]:
        return {} if "FiveStone" not in self.equip_data else {EquipDataProcesser._parse_attributes(str(item["Attrib"]["GeneratedMagic"])): Path(ASSETS + "/image/jx3/attributes/wuxingshi/" + item["Level"] + ".png").as_uri() for item in self.equip_data["FiveStone"]}

    @property
    def peerless(self) -> bool:
        peerless = (self.equip_data["BelongForce"] in ["内功门派", "外功门派"]) \
        or (self.equip_data["MaxStrengthLevel"] == "8") \
        or (self.equip_data["Name"] in EquipDataProcesser.special_weapons) \
        or (any(d.get("Desc") == "atSkillEventHandler" for d in self.equip_data["ModifyType"])) \
        or (self.equip_data.get("Desc", "").startswith("使用：")) \
        or (self.source.startswith("商店：叶鸦"))
        return peerless
    
    @property
    def flicker(self) -> bool:
        return self.equip_data["MaxStrengthLevel"] == "8"

class JX3AttributeParser:
    def __init__(self, role_data: dict, equip_data: dict, name: str, server: str, other_equips: list[AttributeParser] = []):
        self.role = role_data
        equip_map = {
            "帽子": 0, "上衣": 1, "腰带": 2, "护臂": 3, "裤子": 4, 
            "鞋": 5, "项链": 6, "腰坠": 7, "戒指": [8, 9], 
            "投掷囊": 10, "武器": 11, "重剑": 12
        }
        equips_list = [{}] * 13
        rings = iter(equip_map["戒指"])
        data = equip_data["Equips"]
        if len(data) == 12 and Kungfu.with_internel_id(equip_data["Kungfu"]["KungfuID"]).school != "藏剑":
            for equip in data:
                subkind = equip["Icon"]["SubKind"]
                kind = equip["Icon"]["Kind"]
                if subkind == "戒指":
                    equips_list[next(rings)] = equip
                elif subkind in equip_map:
                    equips_list[equip_map[subkind]] = equip
                elif kind == "武器" or (kind == "任务特殊" and subkind == "活动相关"):
                    equips_list[equip_map["武器"]] = equip
            equip_data["Equips"] = equips_list[:12]
        elif len(data) == 13 and Kungfu.with_internel_id(equip_data["Kungfu"]["KungfuID"]).school == "藏剑":
            for equip in data:
                subkind = equip["Icon"]["SubKind"]
                kind = equip["Icon"]["Kind"]
                if subkind == "戒指":
                    equips_list[next(rings)] = equip
                elif subkind in equip_map:
                    equips_list[equip_map[subkind]] = equip
                elif kind == "武器" or (kind == "任务特殊" and subkind == "活动相关"):
                    equips_list[equip_map["武器"]] = equip
            equip_data["Equips"] = equips_list
        else:
            pass
        self.equip = equip_data
        self.info: tuple[str, str] = (name, server)
        self.other_equips = other_equips
        
    @classmethod
    async def player(cls, server: str, name: str, conditions: str = "") -> "JX3AttributeParser | str":
        player_data = (await search_player(role_name=name, server_name=server)).format_jx3api()
        instance = await AttributesRequest.with_name(server, name)
        if not instance:
            return PROMPT.PlayerNotExist
        equip_data = instance.get_equip(conditions)
        if not equip_data:
            return PROMPT.EquipNotFound
        other_equips = instance.get_last_equip()
        return cls(player_data["data"], equip_data["data"], name, server, other_equips)
    
    @property
    def kungfu(self) -> Kungfu:
        return Kungfu.with_internel_id(self.equip["Kungfu"]["KungfuID"])
    
    @property
    def score(self) -> int:
        return self.equip["TotalEquipsScore"]

    @property
    def attr(self) -> dict[str, str]:
        name = self.kungfu.name
        if str(name).endswith("·悟"):
            name = str(name)[:-2]
            if name == "山居问水剑":
                name = "问水诀"
            result = mobile_attribute_calculator(self.equip["Equips"], name or "")
            if self.kungfu.base not in ["治疗", "防御"]:
                result["攻击力"] = result.pop("面板攻击")
                result["基础攻击力"] = result.pop("基础攻击")
            if self.kungfu.base == "治疗":
                result["治疗量"] = result.pop("面板治疗量")
                result.pop("基础治疗量")
            return result
        else:
            return {
                item["name"]: f"{item['value']}%" if item["percent"] else str(item["value"])
                for item in self.equip["PersonalPanel"]
            }

    @property
    def equips(self) -> list[str]:
        equip_list = [
            Equip(each_equip)
            for each_equip
            in self.equip["Equips"]
        ]
        return [
            Template(
                (template_equip if equip_list.index(e) == len(equip_list) - 1 else template_equip + "<div class=\"divider\"></div>")
            ).render(
                icon = e.icon,
                name = e.name,
                attr = e.attr,
                color = e.color,
                quality = e.quality,
                source = e.source,
                strength = e.strength,
                effect = e.effect,
                box = (Path(build_path(ASSETS, ["image", "jx3", "attributes", "not_max_strength.png" if not e.full_strengthen else "max_strength.png"])).as_uri()) if not e.flicker else Path(build_path(ASSETS, ["image", "jx3", "attributes", "flicker.png"])),
                enchants = e.enchants,
                fivestones = e.fivestones,
                peerless = "<img src=\"" + Path(build_path(ASSETS, ["image", "jx3", "attributes", "peerless.png"])).as_uri() +"\" style=\"position: absolute;top: 0; left: -20px;\">" if e.peerless else ""
            )
            for e
            in equip_list
        ]
    
    @property
    def basic_info(self) -> dict[str, str]:
        info = {}
        data = self.role
        info["门派"] = data["forceName"]
        info["体型"] = data["bodyName"]
        info["阵营"] = data["campName"]
        info["心法"] = self.kungfu.name or "未知"
        info["标识"] = data["roleId"]
        info["全服标识"] = data["globalRoleId"]
        return info
    
    @property
    def other_equips_str(self) -> list[str]:
        results = []
        for equip in self.other_equips:
            kungfu_object = Kungfu(equip.kungfu_name)
            prefix = {
                "D": "DPS",
                "T": "T",
                "N": "HPS"
            }[kungfu_object.abbr]
            if equip.kungfu_name in ["惊羽诀", "天罗诡道", "太虚剑意", "紫霞功"]:
                prefix = {
                    "惊羽诀": "JY",
                    "天罗诡道": "TL",
                    "太虚剑意": "JC",
                    "紫霞功": "QC"
                }[equip.kungfu_name]
            results.append(
                Template(template_other).render(
                    icon = kungfu_object.icon,
                    kungfu = equip.kungfu_name,
                    tag = equip.equip_type,
                    score = equip.score,
                    msg = prefix + equip.equip_type
                )
            )
        return results
    
    async def talents(self) -> list[str]:
        qixue_list = self.equip["Person"]["qixueList"]
        unknown_img = build_path(ASSETS, ["image", "jx3", "attributes", "unknown.png"])
        name = ["未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知", "未知"]
        icon = [unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img, unknown_img]
        kungfu = self.kungfu.name
        if kungfu is None:
            return []
        if kungfu.endswith("·悟") and qixue_list == []:
            return []
        if qixue_list == []:
            return []
        for single_qixue in qixue_list:
            location = (await Qixue.create(single_qixue, kungfu)).location
            if location is None:
                continue
            x, y, _icon = location
            name[int(x)-1] = single_qixue["name"]
            icon[int(x)-1] = _icon
        return [
            Template(template_talent).render(
                icon = each_icon,
                name = each_name
            )
            for each_name, each_icon
            in zip(name, icon)
        ]

async def get_attr_v4(server: str, name: str, conditions: str = ""):
    attr_parser = await JX3AttributeParser.player(server, name, conditions)
    if isinstance(attr_parser, str):
        return attr_parser
    basic_attr = {}
    display_required = {
        "D": ["攻击力", "会心", "会心效果", "破防", "无双", "破招", "加速"],
        "N": ["治疗量", "会心", "会心效果", "加速"],
        "T": ["内功防御", "外功防御", "气血", "御劲"]
    }
    detailed_attr = attr_parser.attr
    for a in display_required[attr_parser.kungfu.abbr]:
        if a in detailed_attr:
            basic_attr[a] = detailed_attr.pop(a)
    html = Template(
        read(
            TEMPLATES + "/jx3/attributes_v4.html"
        )
    ).render(
        name = name,
        server= server,
        info = attr_parser.basic_info,
        basic_attr = basic_attr,
        detailed_attr = detailed_attr,
        score = attr_parser.score,
        kungfu_icon = attr_parser.kungfu.icon,
        equips = attr_parser.equips,
        talents = await attr_parser.talents(),
        other_equips = attr_parser.other_equips_str,
        font = ASSETS + "/font/PingFangSC-Semibold.otf",
        saohua = get_saohua()
    )
    return await generate(html, ".container", segment=True, wait_for_network=True, viewport={"height": 1080, "width": 1920})