from functools import cached_property, lru_cache
from typing import Literal, Any, cast, overload
from typing_extensions import Self

from src.const.prompts import PROMPT
from src.const.path import ASSETS, CONST
from src.const.jx3.kungfu import Kungfu
from src.const.jx3.server import Server
from src.utils.file import read
from src.utils.database import attribute_db as db
from src.utils.database.classes import PlayerEquipsCache
from src.utils.network import Request
from src.utils.analyze import R, TuilanData, merge_dicts, parse_luatable, parse_skillevent
from src.utils.exceptions import TabFileMissException

import copy
import re
import json
import zlib
import asyncio
import base64

from src.utils.database.constant import A, B, C, CRITICAL_DAMAGE_DIVISOR, CRITICAL_DIVISOR, DECRITICAL_DAMAGE_DIVISOR, OVERCOME_DIVISOR, SHIELD_130_CONST, STRAIN_DIVISOR, Agility_to_Critical_Cof, AttributesShort, Colors, MaxStrengthLevel, MinStrengthLevel, Spirit_to_Critical_Cof, Spunk_to_Attack_Cof, Spunk_to_BaseOvercome_Cof, Strength_to_Attack_Cof, Strength_to_BaseOvercome_Cof, StrengthIncome
from src.utils.time import Time

def parse_plugin_data(data: str) -> list[dict]:
    def replace_array(m):
        inner = m.group(1)
        return "[" + inner + "]"
    data = data.replace("-", "+").replace("_", "/")
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    decoded = base64.b64decode(data)
    decompressed = zlib.decompress(decoded)
    text = decompressed.decode("utf-8")
    text = re.sub(r"^\{\{", "[{", text)
    text = re.sub(r"\}\}$", "}]", text)
    text = re.sub(r"(\w+)=", r'"\1":', text)
    text = re.sub(r"\{([\d,]*)\}", replace_array, text)
    formatted_data = json.loads(text)
    return formatted_data

def get_attr_name(attribute_name: str):
    return AttributesShort.get(attribute_name, "")

def get_fivestone_level(item_index: int) -> int:
    if item_index in range(24442, 24449+1):
        return item_index - 24441
    elif item_index in range(24423, 24430+1):
        return item_index - 24422
    else:
        raise ValueError(f"无法识别该五行石：5_{item_index}")

def parse_conditions(input_str: str) -> list[str] | Literal[False]:
    input_str = input_str.strip().upper()
    regex = r"(TL|DPS|HPS|PVE|PVP|PVX|QC|JC|JY|T)"
    matches = re.findall(regex, input_str)
    if not matches:
        return False
    t_dps_hps_count = sum(1 for kw in matches if kw in ["T", "DPS", "HPS", "QC", "JC", "TL", "JY"])
    pvp_pve_pvx_count = sum(1 for kw in matches if kw in ["PVP", "PVE", "PVX"])
    if t_dps_hps_count > 1 or pvp_pve_pvx_count > 1:
        return False
    if "T" in matches and ("PVP" in matches or "PVX" in matches):
        return False
    return matches

def read_tab(tab_path: str) -> list[list]:
    with open(tab_path, encoding="gbk", mode="r") as f:
        return [a.strip().split("\t") for a in f.read().strip().split("\n")]

def init_tab_cache():
    TabCache._Attrib = read_tab(ASSETS + "/source/jx3/tabs/Attrib.tab")
    TabCache._Custom_Armor = read_tab(ASSETS + "/source/jx3/tabs/Custom_Armor.tab")
    TabCache._Custom_Trinket = read_tab(ASSETS + "/source/jx3/tabs/Custom_Trinket.tab")
    TabCache._Custom_Weapon = read_tab(ASSETS + "/source/jx3/tabs/Custom_Weapon.tab")
    TabCache._Enchant = read_tab(ASSETS + "/source/jx3/tabs/Enchant.tab")
    TabCache._Set = read_tab(ASSETS + "/source/jx3/tabs/Set.tab")
    TabCache._Item = read_tab(ASSETS + "/source/jx3/tabs/Item.txt")
    TabCache._Other = read_tab(ASSETS + "/source/jx3/tabs/Other.tab")
    TabCache._skill = read_tab(ASSETS + "/source/jx3/tabs/Skill.txt")
    TabCache._skillevent = read_tab(ASSETS + "/source/jx3/tabs/Skillevent.txt")

class TabDescriptor:
    def __init__(self, name):
        self.name = name
    
    def __get__(self, instance, owner):
        if not hasattr(owner, "_initialized") or not owner._initialized:
            init_tab_cache()
            owner._initialized = True
        
        return getattr(owner, f"_{self.name}")


class TabCache:
    Custom_Armor: Any = TabDescriptor("Custom_Armor")
    Custom_Trinket: Any  = TabDescriptor("Custom_Trinket")
    Custom_Weapon: Any  = TabDescriptor("Custom_Weapon")
    Enchant: Any  = TabDescriptor("Enchant")
    Attrib: Any  = TabDescriptor("Attrib")
    Set: Any  = TabDescriptor("Set")
    Item: Any  = TabDescriptor("Item")
    Other: Any  = TabDescriptor("Other")
    skill: Any  = TabDescriptor("skill")
    skillevent: Any  = TabDescriptor("skillevent")
    
    _initialized = False
    
    _Custom_Armor: list[list] = []
    _Custom_Trinket: list[list] = []
    _Custom_Weapon: list[list] = []
    _Enchant: list[list] = []
    _Attrib: list[list] = []
    _Set: list[list] = []
    _Item: list[list] = []
    _Other: list[list] = []
    _skill: list[list] = []
    _skillevent: list[list] = []

    @classmethod
    def force_init(cls):
        """强制初始化所有 Tab 数据"""
        init_tab_cache()
        cls._initialized = True

    @classmethod
    def is_initialized(cls) -> bool:
        """检查是否已经初始化"""
        return cls._initialized


    @classmethod
    @lru_cache(maxsize=None)
    def get_icon_for_equip(cls, ui_id: int) -> tuple[int, str]:
        for each_item in cls.Item:
            if each_item[0] == str(ui_id):
                return int(each_item[1] or 1434), each_item[4]
        raise TabFileMissException(
            f"在 Item.txt 中无法找到 UIID {ui_id} 对应的物品，请检查该 Tab 是否过期！"
        )

    @classmethod
    @lru_cache(maxsize=None)
    def get_icon_for_skill(cls, skill_id: int) -> tuple[int, str]:
        for each_skill in cls.skill:
            if each_skill[0] == str(skill_id):
                return int(each_skill[2]), each_skill[11]
        return (1434, "未知")

    @classmethod
    @lru_cache(maxsize=None)
    def get_equip(cls, equip_id: int, tab_key: Literal[1, 2, 3]) -> list:
        if tab_key == 1:
            tab_file = cls.Custom_Armor
        elif tab_key == 2:
            tab_file = cls.Custom_Trinket
        else:
            tab_file = cls.Custom_Weapon

        for each_equip in tab_file:
            if each_equip[0] == str(equip_id):
                return each_equip
        raise TabFileMissException(
            f"在 装备库Tab 中无法找到 ID {equip_id} 对应的装备，请检查三个装备库 Tab 是否过期！\n装备库 Tab KEY {tab_key}"
        )

    @classmethod
    @lru_cache(maxsize=None)
    def get_attrib(cls, magic_type: int) -> tuple[str, float, float]:
        for each_attrib in cls.Attrib:
            if each_attrib[0] == str(magic_type):
                _min = each_attrib[3]
                _max = each_attrib[4]
                if _min == "":
                    _min = each_attrib[5]
                if _max == "":
                    _max = each_attrib[6]
                if _min == "" or _max == "":
                    _min = 0
                    _max = 0
                return (
                    each_attrib[2],
                    float(_min),
                    float(_max),
                )
        raise TabFileMissException(
            f"在 属性库Tab 中无法找到 ID {magic_type} 对应的属性，请检查 属性库Tab 是否过期！"
        )

    @classmethod
    @lru_cache(maxsize=None)
    def get_enchant(cls, enchant_id: int) -> list:
        for each_enchant in cls.Enchant:
            if each_enchant[0] == str(enchant_id):
                return each_enchant
        raise TabFileMissException(
            f"在 附魔库Tab 中 无法找到 ID {enchant_id} 对应的附魔，请检查 附魔Tab 是否过期！"
        )

    @classmethod
    @lru_cache(maxsize=None)
    def get_colorstone_from_jcl(cls, colorstone_item_index: int) -> tuple[list, int]:
        for each_other in cls.Other:
            if each_other[0] == str(colorstone_item_index):
                ui_id = str(each_other[3])
                for each_enchant in cls.Enchant:
                    if each_enchant[2] == ui_id:
                        return each_enchant, cls.get_icon_for_equip(int(ui_id))[0]
        raise TabFileMissException(
            f"在 附魔库Tab 和 其他物品Tab 中 无法找到 ID {colorstone_item_index} 对应的五彩石，请检查上述 Tab 是否过期！"
        )

    @classmethod
    @lru_cache(maxsize=None)
    def get_colorstone_from_enchant(cls, colorstone_item_index: int) -> tuple[list, int]:
        for each_enchant in cls.Enchant:
            if each_enchant[0] == str(colorstone_item_index):
                return each_enchant, cls.get_icon_for_equip(int(each_enchant[2]))[0]
        raise TabFileMissException(
            f"在 附魔库Tab 中 无法找到 ID {colorstone_item_index} 对应的五彩石，请检查上述 Tab 是否过期！"
        )
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_effect_by_skill_handler_id(cls, skill_handler_id: int) -> str:
        for each_effect in cls.skillevent:
            if each_effect[0] == str(skill_handler_id):
                return parse_skillevent(each_effect[1])
        return ""

    @classmethod
    @lru_cache(maxsize=None)
    def get_set(cls, set_id: int, set_count: int) -> dict[str, float]:
        results = {}
        for each_set in cls.Set:
            if each_set[0] == str(set_id):
                for a in range(1, 8 + 1):
                    index = a * 4
                    if (a + 1) <= set_count:
                        for b in range(1, 4 + 1):
                            c = index + b - 1
                            if c >= len(each_set):
                                break
                            attrib_key = each_set[c]
                            if attrib_key == "":
                                continue
                            modify_type, param1min, param1max = cls.get_attrib(
                                attrib_key
                            )
                            if modify_type in ["atInvalid", ""]:
                                break
                            if modify_type == "atSkillEventHandler":
                                continue
                            results[modify_type] = results.get(modify_type, 0) + float(
                                param1min
                            )
        return results

class Equip:
    equip_sets: dict[int, int] = {}

    @classmethod
    def purge(cls):
        cls.equip_sets = {}

    def _pre_parse(self):
        self.extra_score: float = 0

        self._equip_id = self.jcl_line[2]
        self._strength = self.jcl_line[3]
        self._permanent_enchant = self.jcl_line[5]
        self._common_enchant = self.jcl_line[6]

    def _armor_parse(self):
        diamond_count = 2
        self._diamonds = [get_fivestone_level(k[1]) for k in self.jcl_line[4][:diamond_count]]
        armor_data = TabCache.get_equip(self._equip_id, 1)

        self._max_strength = int(armor_data[104])

        self._quality = int(armor_data[11])
        self._ui_id = int(armor_data[2])

        color = int(armor_data[21])

        if str(self.jcl_line[0]) in ["3", "10"]:
            if color == 4:
                equip_score = int(self._quality * 1.8 + 0.5)
        elif str(self.jcl_line[0]) in ["4"]:
            if color == 4:
                equip_score = int(self._quality * 1.62 + 0.5)
        else:
            if color == 4:
                equip_score = int(self._quality * 1.26 + 0.5)
        
        self._source = f"{armor_data[73]}：{armor_data[72]}"

        self.score += int(equip_score)
        self.extra_score += int((1/2) * equip_score * self._strength * (0.003 * self._strength + 0.007) + 0.5)

        diamond_index = 0

        self._color = Colors[int(armor_data[21])]

        if armor_data[70] == "精简" or \
            armor_data[68] != "":
            self._peerless = True

        if armor_data[19]:
            set_id = int(armor_data[19])
            Equip.equip_sets[set_id] = Equip.equip_sets.get(set_id, 0) + 1

        # Base
        for i in [k for k in range(22, 37+1) if (k - 22) % 3 == 0]:
            base_type = armor_data[i]
            if base_type in ["atInvalid", ""]:
                break
            base_min = float(armor_data[i+1])
            # base_max = float(armor_data[i+2])
            self.attributes[base_type] = self.attributes.get(base_type, 0) + int(base_min)
        
        # Magic
        for i in range(52, 67+1):
            attrib_key = armor_data[i]
            if attrib_key == "":
                break
            modify_type, param1min, param1max = TabCache.get_attrib(attrib_key)
            if modify_type in ["atInvalid", ""]:
                break
            if modify_type == "atSkillEventHandler":
                self._peerless = True
                self.skill_event_handler = int(param1min)
                continue
            if modify_type in AttributesShort:
                self._attribute.append(
                    get_attr_name(modify_type)
                )
            final_value = param1min + R(param1min * StrengthIncome[self._strength])
            self.attributes[modify_type] = self.attributes.get(modify_type, 0) + int(final_value)

        # Diamond
        for i in [k for k in range(97, 100+1) if k % 2 == 1]:
            diamond_attrib_id = int(armor_data[i])
            if diamond_attrib_id == 0:
                break
            modify_type, param1min, param1max = TabCache.get_attrib(diamond_attrib_id)
            diamond_level = self._diamonds[diamond_index]
            diamond_index += 1
            self._diamonds_with_attr.append(
                (get_attr_name(modify_type), diamond_level)
            )
            if diamond_level > 6:
                diamond_extra_score = (1.3 * (0.65 * diamond_level - 3.2) * A * B)
                final_value = 1.3 * (0.65 * diamond_level - 3.2) * MaxStrengthLevel / MinStrengthLevel * param1min
            else:
                diamond_extra_score = (0.195 * diamond_level) * A * B
                final_value = 0.195 * diamond_level * MaxStrengthLevel / MinStrengthLevel * param1min
            self.extra_score += diamond_extra_score * MaxStrengthLevel / MinStrengthLevel
            final_value = int(final_value)
            self.attributes[modify_type] = self.attributes.get(modify_type, 0) + final_value

    def _trinket_parse(self):
        if str(self.jcl_line[0]) not in ["6", "7"]:
            self._diamonds = [get_fivestone_level(k[1]) for k in self.jcl_line[4][:1]]
        else:
            self._diamonds = []
        trinket_data = TabCache.get_equip(self._equip_id, 2)

        self._max_strength = int(trinket_data[104])

        self._quality = int(trinket_data[11])
        self._ui_id = int(trinket_data[2])

        color = int(trinket_data[21])

        if color == 4:
            equip_score = int(0.9 * self._quality + 0.5)
        elif color == 5:
            equip_score = int(1.25 * self._quality + 0.5)
        
        self._source = f"{trinket_data[73]}：{trinket_data[72]}"

        self.score += int(equip_score)
        self.extra_score += int((1/2) * equip_score * self._strength * (0.003 * self._strength + 0.007) + 0.5)

        diamond_index = 0

        self._color = [
            "(167, 167, 167)",
            "(255, 255, 255)",
            "(0, 210, 75)",
            "(0, 126, 255)",
            "(254, 45, 254)",
            "(255, 165, 0)",
        ][int(trinket_data[21])]

        if trinket_data[70] == "精简" or \
            trinket_data[68] != "":
            self._peerless = True

        if trinket_data[19]:
            set_id = int(trinket_data[19])
            Equip.equip_sets[set_id] = Equip.equip_sets.get(set_id, 0) + 1

        # Base
        for i in [k for k in range(22, 37+1) if k % 3 == 0]:
            base_type = trinket_data[i]
            if base_type in ["atInvalid", ""]:
                break
            base_min = float(trinket_data[i+1])
            # base_max = float(trinket_data[i+2])
            self.attributes[base_type] = self.attributes.get(base_type, 0) + int(base_min)
        
        # Magic
        for i in range(52, 67+1):
            attrib_key = trinket_data[i]
            if attrib_key == "":
                break
            modify_type, param1min, param1max = TabCache.get_attrib(attrib_key)
            if modify_type in ["atInvalid", ""]:
                break
            if modify_type == "atSkillEventHandler":
                self._peerless = True
                self.skill_event_handler = int(param1min)
                continue
            if modify_type in AttributesShort:
                self._attribute.append(
                    get_attr_name(modify_type)
                )
            final_value = param1min + R(param1min * StrengthIncome[self._strength])
            self.attributes[modify_type] = self.attributes.get(modify_type, 0) + int(final_value)

        # Diamond
        if str(self.jcl_line[0]) not in ["6", "7"]:
            for i in [k for k in range(99, 103+1) if k % 2 == 1]:
                diamond_attrib_id = int(trinket_data[i])
                if diamond_attrib_id == 0:
                    break
                modify_type, param1min, param1max = TabCache.get_attrib(diamond_attrib_id)
                diamond_level = self._diamonds[diamond_index]
                diamond_index += 1
                self._diamonds_with_attr.append(
                    (get_attr_name(modify_type), diamond_level)
                )
                if diamond_level > 6:
                    diamond_extra_score = (1.3 * (0.65 * diamond_level - 3.2) * A * B)
                    final_value = 1.3 * (0.65 * diamond_level - 3.2) * MaxStrengthLevel / MinStrengthLevel * param1min
                else:
                    diamond_extra_score = (0.195 * diamond_level) * A * B
                    final_value = 0.195 * diamond_level * MaxStrengthLevel / MinStrengthLevel * param1min
                self.extra_score += diamond_extra_score * MaxStrengthLevel / MinStrengthLevel
                final_value = int(final_value)
                self.attributes[modify_type] = self.attributes.get(modify_type, 0) + final_value

    def _weapon_parse(self):
        if str(self.jcl_line[0]) not in ["0", "1"]:
            self._diamonds = [get_fivestone_level(self.jcl_line[4][0][1])]
        else:
            if self._diamonds == []:
                self._diamonds = [get_fivestone_level(k[1]) for k in self.jcl_line[4][:3]]
        weapon_data = TabCache.get_equip(self._equip_id, 3)

        self._max_strength = int(weapon_data[104])

        self._quality = int(weapon_data[12])
        self._ui_id = int(weapon_data[2])

        color = int(weapon_data[22])

        if str(self.jcl_line[0]) in ["0", "1"]:
            if color == 4:
                equip_score = int(2.16 * self._quality + 0.5)
            elif color == 5:
                equip_score = int(3 * self._quality + 0.5)
        else:
            equip_score = int(1.08 * self._quality + 0.5)
        
        self._source = f"{weapon_data[74]}：{weapon_data[73]}"

        self.score += int(equip_score)
        self.extra_score += int((1/2) * equip_score * self._strength * (0.003 * self._strength + 0.007) + 0.5)

        diamond_index = 0

        self._color = [
            "(167, 167, 167)",
            "(255, 255, 255)",
            "(0, 210, 75)",
            "(0, 126, 255)",
            "(254, 45, 254)",
            "(255, 165, 0)",
        ][int(weapon_data[22])]

        if weapon_data[71] == "精简" or \
            weapon_data[69] != "":
            self._peerless = True

        if weapon_data[20]:
            set_id = int(weapon_data[20])
            Equip.equip_sets[set_id] = Equip.equip_sets.get(set_id, 0) + 1

        # Base
        for i in [k for k in range(23, 29+1) if (k - 23) % 3 == 0]:
            base_type = weapon_data[i]
            if base_type in ["atInvalid", ""]:
                break
            base_min = float(weapon_data[i+1])
            # base_max = float(weapon_data[i+2])
            self.attributes[base_type] = self.attributes.get(base_type, 0) + int(base_min)
        
        # Magic
        for i in range(53, 67+1):
            attrib_key = weapon_data[i]
            if attrib_key == "":
                break
            modify_type, param1min, param1max = TabCache.get_attrib(attrib_key)
            if modify_type in ["atInvalid", ""]:
                break
            if modify_type == "atSkillEventHandler":
                self._peerless = True
                self.skill_event_handler = int(param1min)
                continue
            if modify_type in AttributesShort:
                self._attribute.append(
                    get_attr_name(modify_type)
                )
            final_value = param1min + R(param1min * StrengthIncome[self._strength])
            self.attributes[modify_type] = self.attributes.get(modify_type, 0) + int(final_value)

        # Diamond
        for i in [k for k in range(97, 101+1) if k % 2 == 1]:
            diamond_attrib_id = int(weapon_data[i])
            if diamond_attrib_id == 0:
                break
            modify_type, param1min, param1max = TabCache.get_attrib(diamond_attrib_id)
            diamond_level = self._diamonds[diamond_index]
            self._diamonds_with_attr.append(
                (get_attr_name(modify_type), diamond_level)
            )
            diamond_index += 1
            if diamond_level > 6:
                diamond_extra_score = (1.3 * (0.65 * diamond_level - 3.2) * A * B)
                final_value = 1.3 * (0.65 * diamond_level - 3.2) * MaxStrengthLevel / MinStrengthLevel * param1min
            else:
                diamond_extra_score = (0.195 * diamond_level) * A * B
                final_value = 0.195 * diamond_level * MaxStrengthLevel / MinStrengthLevel * param1min
            diamonds_total_score = diamond_extra_score * MaxStrengthLevel / MinStrengthLevel
            self.extra_score += diamonds_total_score
            final_value = int(final_value)
            self.attributes[modify_type] = self.attributes.get(modify_type, 0) + final_value
        
        # ColorStone
        if str(self.jcl_line[0]) in ["0", "1"]:
            if self._color_stone == 0:
                self._color_stone_source = (self.jcl_line[4][3][0] == 0)
                self._color_stone = self.jcl_line[4][3][1]
            if self._color_stone_source:
                colorstone_data, self._color_stone_icon = TabCache.get_colorstone_from_enchant(self._color_stone)
            else:
                colorstone_data, self._color_stone_icon = TabCache.get_colorstone_from_jcl(self._color_stone)
            self._color_stone_name = colorstone_data[1]
            color_stone_level = ["壹", "貳", "叁", "肆", "伍", "陆"].index(self._color_stone_name[-2]) + 1
            self.extra_score += 3.5*A*C*color_stone_level
            for i in (4, 12, 19):
                attr_name = colorstone_data[i]
                if attr_name == "":
                    break
                attr_value = float(colorstone_data[i+1])
                self.attributes[attr_name] = self.attributes.get(attr_name, 0) + int(attr_value)
    
    def _post_parse(self):
        self._icon, self._name = TabCache.get_icon_for_equip(self._ui_id)
        self.score += int(self.extra_score + 0.5)
        if int(self._permanent_enchant) != 0:
            enchant_data = TabCache.get_enchant(self._permanent_enchant) 
            self._permanent_enchant_name = enchant_data[1]
            attr_name = enchant_data[4]
            attr_value = float(enchant_data[5])
            self.attributes[attr_name] = self.attributes.get(attr_name, 0) + int(attr_value)
            self.score += int(enchant_data[7] or 0)
        if int(self._common_enchant) != 0:
            enchant_data = TabCache.get_enchant(self._common_enchant)
            self._common_enchant_name = enchant_data[1]
            self.score += int(enchant_data[7] or 0)

    @property
    def icon(self) -> str:
        return f"https://icon.jx3box.com/icon/{self._icon}.png"
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def color(self) -> str:
        return self._color
    
    @property
    def attribute(self) -> str:
        return " ".join([a for a in self._attribute if a != "体质"])
    
    @property
    def quality(self) -> int:
        return self._quality
    
    @property
    def permanent_enchant(self) -> str:
        return self._permanent_enchant_name

    @property
    def common_enchant(self) -> str:
        return self._common_enchant_name

    @property
    def color_stone(self) -> str:
        return self._color_stone_name

    @property
    def color_stone_icon(self) -> str:
        return f"https://icon.jx3box.com/icon/{self._color_stone_icon}.png"
    
    @property
    def peerless(self) -> bool:
        return self._peerless
    
    @property
    def strength(self) -> int:
        return self._strength
    
    @property
    def max_strength(self) -> int:
        return self._max_strength
    
    @property
    def diamonds(self) -> list[tuple[str, int]]:
        return self._diamonds_with_attr
    
    @property
    def source(self) -> str:
        return self._source
    
    @cached_property
    def effect(self) -> str:
        text = TabCache.get_effect_by_skill_handler_id(self.skill_event_handler)
        idx = text.rfind("。", 0, text.rfind("。"))
        if idx == -1:
            return text
        return text[:idx+1]

    def __init__(self, jcl_line: list):
        self.jcl_line = jcl_line
        self.location_index = int(jcl_line[0])
        self.attributes: dict[str, int] = {}
        self.score: int = 0

        self.skill_event_handler: int = 0

        self._ui_id: int = 0
        self._icon: int = 0
        self._name: str = ""
        self._color: str = ""
        self._attribute: list[str] = []
        self._quality: int = 0
        self._strength: int = 0
        self._diamonds: list[int] = []
        self._permanent_enchant: int = 0
        self._permanent_enchant_name: str = ""
        self._common_enchant: int = 0
        self._common_enchant_name: str = ""
        self._color_stone: int = 0
        self._color_stone_name: str = ""
        self._color_stone_icon: int = 0
        self._color_stone_source: bool = False # False JCL True Tuilan
        self._peerless: bool = False
        self._max_strength: int = 0
        self._diamonds_with_attr: list[tuple[str, int]] = []
        self._source: str = ""

    def parse(self):
        equip_index = self.jcl_line[0]
        if equip_index in [3, 4, 8, 10, 11, 12]: # 上衣 帽子 腰带 下装 鞋子 护腕
            self._armor_parse()
        elif equip_index in [5, 6, 7, 9]: # 项链 戒指 戒指 腰坠
            self._trinket_parse()
        else: # 武器（可能包含藏剑） 暗器
            self._weapon_parse()

class Talent:
    def __init__(self, skill_id: int):
        self.skill_id = skill_id
        self.icon_id, self.name = TabCache.get_icon_for_skill(skill_id)
    
    @property
    def icon(self):
        return f"https://icon.jx3box.com/icon/{self.icon_id}.png"

class FinalAttr:
    def __init__(
            self,
            equip_attr: dict[str, int],
            kungfu_id: int
        ):
        self.equip_attr: dict[str, int] = equip_attr
        self.kungfu_id = kungfu_id
        self.attr: dict[str, float] = {
            "atSpiritBase": 44,
            "atStrengthBase": 44,
            "atAgilityBase": 44,
            "atSpunkBase": 44,
            "atVitalityBase": 45
        }
        if "atBasePotentialAdd" in equip_attr: # 全属性
            for each_basic_attr in self.attr:
                self.attr[each_basic_attr] += equip_attr["atBasePotentialAdd"]

    def get_kungfu_base(self):
        if self.kungfu_id in [10014, 10081, 10447, 10175, 10627, 10821]: # 根骨
            return "atSpiritBase"
        elif self.kungfu_id in [10003, 10225, 10242, 10615, 10021, 10786]: # 元气
            return "atSpunkBase"
        elif self.kungfu_id in [10015, 10533, 10144, 10585, 10390, 10756]: # 身法
            return "atAgilityBase"
        elif self.kungfu_id in [10224, 10698, 10026, 10268, 10464]: # 力道
            return "atStrengthBase"
        elif self.kungfu_id in [10062, 10002, 10243, 10389]: # 体质
            return "atVitalityBase"
        elif self.kungfu_id in [10080, 10028, 10176, 10448, 10626]: # 治疗
            return "atSpiritBase"
        else:
            raise
    
    @property
    def kungfu_type(self) -> str:
        main_attr = self.get_kungfu_base()
        if main_attr in ["atSpiritBase", "atSpunkBase"] or self.kungfu_id in [10243, 10002]:
            return "Magic"
        else:
            return "Physics"
        
    @property
    def extra_base_attack(self) -> dict[str, float]:
        # 额外的基础攻击 由元气和力道提供
        return {
            "atPhysicsAttackPowerBase": self.attr.get("atStrengthBase", 44) * Strength_to_Attack_Cof,
            "atMagicAttackPowerBase": self.attr.get("atSpunkBase", 44) * Spunk_to_Attack_Cof
        }
    
    @property
    def extra_base_overcome(self) -> dict[str, float]:
        # 额外的基础破防 由元气和力道提供
        return {
            "atPhysicsOvercomeBase": self.attr.get("atStrengthBase", 44) * Strength_to_BaseOvercome_Cof,
            "atMagicOvercome": self.attr.get("atSpunkBase", 44) * Spunk_to_BaseOvercome_Cof
        }
    
    @property
    def extra_critical(self) -> dict[str, float]:
        # 额外的会心等级 由身法和根骨提供
        return {
            "atPhysicsCriticalStrike": self.attr.get("atAgilityBase", 44) * Agility_to_Critical_Cof,
            "atMagicCriticalStrike": self.attr.get("atSpiritBase", 44) * Spirit_to_Critical_Cof
        }
        
    def output_attr(self) -> dict[str, str]:
        self.equip_attr.pop("atSkillEventHandler", None) # 套装效果（施展招式）
        self.equip_attr.pop("atSetEquipmentRecipe", None) # 套装效果（伤害提高）
        self.equip_attr.pop("atPVXAllRound", None) # 煞笔全能
        kungfu_name = str(Kungfu.with_internel_id(self.kungfu_id).name)
        if kungfu_name == "山居问水剑·悟":
            kungfu_name = "问水诀"
        if kungfu_name.endswith("·悟"):
            kungfu_name = kungfu_name[:-2]
        self.attr = merge_dicts(
            copy.deepcopy(Kungfu.kungfu_basic[kungfu_name]),
            self.attr
        )
        self.attr = merge_dicts(
            cast(dict[str, float], self.equip_attr),
            self.attr
        )

        self.attr = merge_dicts(
            self.attr, self.extra_base_attack
        )
        self.attr = merge_dicts(
            self.attr, self.extra_base_overcome
        )
        self.attr = merge_dicts(
            self.attr, self.extra_critical
        )

        kungfu_main_attr = self.get_kungfu_base()
        weapon_damage = int(self.attr.get("atMeleeWeaponDamageBase", 0) + self.attr.get("atMeleeWeaponDamageRand", 0) / 2)
        attack = max(
            int(self.attr.get("atPhysicsAttackPowerBase", 0)), # 外功基础攻击

            int(self.attr.get("atLunarAttackPowerBase", 0)) + \
            int(self.attr.get("atMagicAttackPowerBase", 0)) + \
            int(self.attr.get("atSolarAndLunarAttackPowerBase", 0)), # 阴性基础攻击 内功基础攻击 阴阳基础攻击

            int(self.attr.get("atSolarAttackPowerBase", 0)) + \
            int(self.attr.get("atMagicAttackPowerBase", 0)) + \
            int(self.attr.get("atSolarAndLunarAttackPowerBase", 0)), # 阳性基础攻击 内功基础攻击 阴阳基础攻击
            
            int(self.attr.get("atNeutralAttackPowerBase", 0)) + \
            int(self.attr.get("atMagicAttackPowerBase", 0)), # 混元基础攻击 内功基础攻击

            int(self.attr.get("atPoisonAttackPowerBase", 0)) + \
            int(self.attr.get("atMagicAttackPowerBase", 0)) # 毒性基础攻击 内功基础攻击
        )
        base_therapy = self.attr.get("atTherapyPowerBase", 0)
        final_therapy = copy.deepcopy(base_therapy)
        final_attack = copy.deepcopy(attack)
        critical = max(
            int(self.attr.get("atPhysicsCriticalStrike", 0)) + \
            int(self.attr.get("atAllTypeCriticalStrike", 0)), # 外功会心 全会心

            int(self.attr.get("atLunarCriticalStrike", 0)) + \
            int(self.attr.get("atMagicCriticalStrike", 0)) + \
            int(self.attr.get("atSolarAndLunarCriticalStrike", 0)) + \
            int(self.attr.get("atAllTypeCriticalStrike", 0)), # 阴性会心 内功会心 阴阳会心 全会心

            int(self.attr.get("atSolarCriticalStrike", 0)) + \
            int(self.attr.get("atMagicCriticalStrike", 0)) + \
            int(self.attr.get("atSolarAndLunarCriticalStrike", 0)) + \
            int(self.attr.get("atAllTypeCriticalStrike", 0)), # 阳性会心 内功会心 阴阳会心 全会心

            int(self.attr.get("atNeutralCriticalStrike", 0)) + \
            int(self.attr.get("atMagicCriticalStrike", 0)) + \
            int(self.attr.get("atAllTypeCriticalStrike", 0)), # 混元会心 内功会心 全会心

            int(self.attr.get("atPoisonCriticalStrike", 0)) + \
            int(self.attr.get("atMagicCriticalStrike", 0)) + \
            int(self.attr.get("atAllTypeCriticalStrike", 0)), # 毒性会心 内功会心 全会心
        )
        critical_damage = max(
            int(self.attr.get("atPhysicsCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atAllTypeCriticalDamagePowerBase", 0)), # 外功会效 全会效

            int(self.attr.get("atLunarCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atMagicCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atSolarAndLunarCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atAllTypeCriticalDamagePowerBase", 0)), # 阴性会效 内功会效 阴阳会效 全会效
            
            int(self.attr.get("atSolarCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atMagicCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atSolarAndLunarCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atAllTypeCriticalDamagePowerBase", 0)), # 阳性会效 内功会效 阴阳会心 全会效
            
            int(self.attr.get("atNeutralCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atMagicCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atAllTypeCriticalDamagePowerBase", 0)), # 混元会效 内功会效 全会效
            
            int(self.attr.get("atPoisonCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atMagicCriticalDamagePowerBase", 0)) + \
            int(self.attr.get("atAllTypeCriticalDamagePowerBase", 0)), # 毒性会效 内功会效 全会效
        )
        base_overcome = max(
            int(self.attr.get("atPhysicsOvercomeBase", 0)), # 外功破防

            int(self.attr.get("atLunarOvercomeBase", 0)) + \
            int(self.attr.get("atMagicOvercome", 0)) + \
            int(self.attr.get("atSolarAndLunarOvercomeBase", 0)), # 阴性基础破防 内功基础破防 阴阳基础破防
            
            int(self.attr.get("atSolarOvercomeBase", 0)) + \
            int(self.attr.get("atMagicOvercome", 0)) + \
            int(self.attr.get("atSolarAndLunarOvercomeBase", 0)), # 阳性基础破防 内功基础破防 阴阳基础破防
            
            int(self.attr.get("atNeutralOvercomeBase", 0)) + \
            int(self.attr.get("atMagicOvercome", 0)), # 混元基础破防 内功基础破防
            
            int(self.attr.get("atPoisonOvercomeBase", 0)) + \
            int(self.attr.get("atMagicOvercome", 0)) # 毒性基础破防 内功基础破防
        )
        final_overcome = copy.deepcopy(base_overcome)
        strain = int(self.attr.get("atStrainBase", 0))
        haste = int(self.attr.get("atHasteBase", 0))
        surplus = int(self.attr.get("atSurplusValueBase", 0))
        base_vitality = int(self.attr.get("atVitalityBase", 0))
        vitality = int(
            base_vitality * \
            (1 + int(self.attr.get("atVitalityBasePercentAdd", 0)) / 1024)
        )
        base_spirit = int(self.attr.get("atSpiritBase", 0))
        spirit = int(
            base_spirit * \
            (1 + int(self.attr.get("atSpiritBasePercentAdd", 0)) / 1024)
        )
        physics_shield = self.attr.get("atPhysicsShieldBase", 0)
        magic_shield = self.attr.get("atMagicShield", 0)
        toughness = self.attr.get("atToughnessBase", 0)
        decritical_damage = self.attr.get("atDecriticalDamagePowerBase", 0)
        for attr_name, attr_value in Kungfu.kungfu_coefficient[kungfu_name].items():
            if attr_name == "Attack":
                final_attack += int(self.attr.get(kungfu_main_attr, 0) * attr_value / 1024)
            elif attr_name == "Critical":
                critical += int(self.attr.get(kungfu_main_attr, 0) * attr_value / 1024)
            elif attr_name == "Overcome":
                final_overcome += int(self.attr.get(kungfu_main_attr, 0) * attr_value / 1024)
            elif attr_name == "PhysicsShield":
                physics_shield += int(self.attr.get(kungfu_main_attr, 0) * attr_value / 1024)
            elif attr_name == "MagicShield":
                magic_shield += int(self.attr.get(kungfu_main_attr, 0) * attr_value / 1024)
            elif attr_name == "Therapy":
                final_therapy += int(self.attr.get(kungfu_main_attr, 0) * attr_value / 1024)
        abbr = Kungfu(kungfu_name).abbr
        if abbr == "D":
            return {
                "攻击力": str(final_attack),
                "基础攻击力": str(attack),
                "会心": str(R(critical / CRITICAL_DIVISOR * 100, 2)) + "%",
                "会心效果": str(R((critical_damage / CRITICAL_DAMAGE_DIVISOR + 1.75) * 100, 2)) + "%",
                "加速": str(haste),
                get_attr_name(kungfu_main_attr): str(self.attr.get(kungfu_main_attr, 0)),
                "破防": str(R(final_overcome / OVERCOME_DIVISOR * 100, 2)) + "%",
                "无双": str(R(strain / STRAIN_DIVISOR * 100, 2)) + "%",
                "破招": str(surplus),
                "武器伤害": str(weapon_damage),
                "御劲": str(R(toughness / CRITICAL_DIVISOR * 100, 2)) + "%",
                "化劲": str(round((int((decritical_damage / (decritical_damage + DECRITICAL_DAMAGE_DIVISOR)) * 1024) + 102) * 100 / 1024, 2)) + "%"
            }
        elif abbr == "N":
            return {
                "治疗量": str(final_therapy),
                "基础治疗量": str(base_therapy),
                "会心": str(R(critical / CRITICAL_DIVISOR * 100, 2)) + "%",
                "会心效果": str(R((critical_damage / CRITICAL_DAMAGE_DIVISOR + 1.75) * 100, 2)) + "%",
                "加速": str(haste),
                "根骨": str(spirit),
                "破防": str(R(final_overcome / OVERCOME_DIVISOR * 100, 2)) + "%",
                "无双": str(R(strain / STRAIN_DIVISOR * 100, 2)) + "%",
                "破招": str(surplus),
                "基础根骨": str(base_spirit),
                "御劲": str(R(toughness / CRITICAL_DIVISOR * 100, 2)) + "%",
                "化劲": str(round((int((decritical_damage / (decritical_damage + DECRITICAL_DAMAGE_DIVISOR)) * 1024) + 102) * 100 / 1024, 2)) + "%"
            }
        else:
            return {
                "内功防御": str(R(magic_shield / (magic_shield + SHIELD_130_CONST) * 100, 2)) + "%",
                "外功防御": str(R(physics_shield / (physics_shield + SHIELD_130_CONST) * 100, 2)) + "%",
                "会心": str(R(critical / CRITICAL_DIVISOR * 100, 2)) + "%",
                "会心效果": str(R((critical_damage / CRITICAL_DAMAGE_DIVISOR + 1.75) * 100, 2)) + "%",
                "加速": str(haste),
                "体质": str(vitality),
                "破防": str(R(final_overcome / OVERCOME_DIVISOR * 100, 2)) + "%",
                "无双": str(R(strain / STRAIN_DIVISOR * 100, 2)) + "%",
                "破招": str(surplus),
                "基础体质": str(base_vitality),
                "御劲": str(R(toughness / CRITICAL_DIVISOR * 100, 2)) + "%",
                "化劲": str(round((int((decritical_damage / (decritical_damage + DECRITICAL_DAMAGE_DIVISOR)) * 1024)) * 100 / 1024, 2)) + "%"
            }

class JX3PlayerAttribute:
    @classmethod
    async def from_jx3api(cls, server: str, name: str, url_require: bool = False) -> Self | str:
        if not url_require:
            raw_data = {}
            raw_data["code"] = 404
        else:
            url = read(CONST + "/cache/attribute.txt")
            params = {
                "server": server,
                "name": name,
                "format": "client"
            }
            raw_data = (await Request(url, params=params).get()).json()
        if raw_data["code"] != 200:
            return PROMPT.PlayerNotExist
        results = []
        
        for each_equip in raw_data["data"]["equip_list"]:
            position_id = each_equip["nItemIndex"]
            
            if position_id not in range(0, 12+1):
                continue

            tab_type = each_equip["dwTabType"]
            tab_index = each_equip["dwTabIndex"]
            strength_level = each_equip["nStrengthLevel"]
            
            diamonds = []

            for each_diamond in each_equip.get("aSlotItem", []):
                diamonds.append(
                    each_diamond
                )
            
            if position_id == 0:
                diamonds.append(
                    each_equip["ColorInfo"][0]
                )

            permanent_enchant_id = each_equip["dwPermanentEnchantID"]
            common_enchant_id = each_equip["dwTemporaryEnchantID"]
            
            results.append(
                [
                    position_id,
                    tab_type,
                    tab_index,
                    strength_level,
                    diamonds,
                    permanent_enchant_id,
                    common_enchant_id,
                    0
                ]
            )

        instance = cls(
            results,
            [],
            int(raw_data["data"]["kungfu_id"]),
            int(raw_data["data"]["global_id"])
        )
        instance.save()

    @classmethod
    async def from_tuilan(cls, role_id: str, server_name: str, global_role_id: str) -> None:
        params = {
            "zone": Server(server_name).zone,
            "server": Server(server_name).server,
            "game_role_id": role_id
        }
        data = (await Request("https://m.pvp.xoyo.com/mine/equip/get-role-equip", params=params).post(tuilan=True)).json()
        if data["code"] != 0:
            return None
        jcl_lines = TuilanData(data).output_jcl_line()
        
        instance = cls(
            jcl_lines, [],
            cast(int, Kungfu.with_internel_id(int(data["data"]["Kungfu"]["KungfuID"]), True).id),
            int(global_role_id)
        )
        instance.save()

    @classmethod
    async def frmo_jcl_line(cls, jcl_line: str) -> Self:
        lua_table = cast(list, parse_luatable(jcl_line))
        equips_lines = [e for e in lua_table[5] if int(e[0]) in range(0, 12+1)]
        talents_lines = [int(t[1]) for t in lua_table[6]]
        if lua_table[7]:
            global_role_id = int(lua_table[7])
        else:
            global_role_id = 1145141919810
        result = cls(
            equips_lines, talents_lines,
            cast(int, Kungfu.with_internel_id(int(lua_table[3]), True).id),
            global_role_id,
            name=lua_table[1]
        )
        return result
    
    @classmethod
    async def from_plugin(cls, data: str, kungfu_id: int, global_role_id: int) -> Self:
        equips_data = parse_plugin_data(data)
        equips_lines = []
        for each_equip in equips_data:
            if each_equip["nPos"] not in range(0, 12 + 1):
                continue
            if each_equip["nPos"] == 1 and kungfu_id not in [10144, 10145]:
                continue
            diamonds = []
            for each_diamond in each_equip["aDiamondEnchant"]:
                if each_diamond in range(6210, 6217 + 1):
                    diamonds.append(
                        [
                            5,
                            each_diamond - 6210 + 24441
                        ]
                    )
                elif each_diamond == 6218:
                    diamonds.append(
                        [
                            5,
                            24449
                        ]
                    )
                else:
                    diamonds.append(
                        [
                            5,
                            each_diamond - 6218 + 24441 + 1
                        ]
                    )
            if each_equip["dwItemFEAEnchantID"] != 0:
                diamonds.append(
                    [
                        0,
                        each_equip["dwItemFEAEnchantID"]
                    ]
                )
            equips_lines.append(
                [
                    int(each_equip["nPos"]),
                    int(each_equip["dwTabType"]),
                    int(each_equip["dwTabIndex"]),
                    int(each_equip["nStrengthLevel"]),
                    diamonds,
                    int(each_equip["dwPermanentEnchantID"]),
                    int(each_equip["dwTemporaryEnchantID"]),
                    0
                ]
            )
        return cls(
            equips_lines,
            [],
            kungfu_id,
            global_role_id
        )

    @classmethod
    async def from_jcl(cls, jcl_content: str) -> list[Self]:
        jcl_lines = jcl_content.strip().split("\n")
        player_info_lines: dict[int, list] = {}
        player_name: dict[int, str] = {}
        for each_jcl_line in jcl_lines:
            parts = each_jcl_line.strip().split("\t")
            if len(parts) < 6 or parts[4] != "4":
                continue
            lua_table_raw = parts[5]
            try:
                lua_table = cast(list, await asyncio.to_thread(parse_luatable, lua_table_raw))
            except Exception:
                continue
            if len(lua_table) >= 8:
                try:
                    global_role_id = int(lua_table[7])
                except TypeError:
                    continue
                player_name[global_role_id] = lua_table[1]
                if global_role_id not in player_info_lines or len(player_info_lines[global_role_id]) < len(lua_table):
                    player_info_lines[global_role_id] = lua_table

        async def build_attr(global_role_id: int, lua_table: list):
            equips_lines = [e for e in lua_table[5] if int(e[0]) in range(0, 13)]
            talents_lines = [int(t[1]) for t in lua_table[6]]
            return cls(
                equips_lines,
                talents_lines,
                cast(int, Kungfu.with_internel_id(int(lua_table[3]), True).id),
                global_role_id,
                name=player_name.get(global_role_id, "未知")
            )

        tasks = [build_attr(rid, lua) for rid, lua in player_info_lines.items()]
        return await asyncio.gather(*tasks)

    @overload
    @classmethod
    async def from_database(cls, global_role_id: int, tag: str = "", all: Literal[False] = False) -> Self | None: ...

    @overload
    @classmethod
    async def from_database(cls, global_role_id: int, tag: str = "", all: Literal[True] = True) -> list[Self] | None: ...

    @classmethod
    async def from_database(cls, global_role_id: int, tag: str = "", all: bool = False) -> Self | list[Self] | None:
        tags = parse_conditions(tag)
        all_equips: list[PlayerEquipsCache] | Any = db.where_all(PlayerEquipsCache(), "global_role_id = ?", str(global_role_id), default=[])
        if not all_equips:
            return None
        final_equips = copy.deepcopy(all_equips)
        final_equip: PlayerEquipsCache | None = None
        if not tags:
            final_equip = max(final_equips, key=lambda x: x.timestamp)
        else:
            for each_tag in ["PVE", "PVP", "PVX"]:
                if each_tag in tags:
                    final_equips = [e for e in final_equips if e.tag == each_tag]
            for each_equip in final_equips:
                if each_equip.kungfu_id in [10014, 10015, 10224, 10225]:
                    if (
                        ("QC" in tags and each_equip.kungfu_id == 10014) or \
                        ("JC" in tags and each_equip.kungfu_id == 10015) or \
                        ("JY" in tags and each_equip.kungfu_id == 10224) or \
                        ("TL" in tags and each_equip.kungfu_id == 10225) or \
                        ("WX" in tags and each_equip.kungfu_id == 10821)
                    ):
                        final_equip = each_equip
                        break
                else:
                    kungfu_tag = {"D": "DPS", "T": "T", "N": "HPS"}[Kungfu.with_internel_id(each_equip.kungfu_id).abbr]
                    if kungfu_tag in tags:
                        final_equip = each_equip
                        break
        if final_equip is None:
            return None
        if all:
            results: list[PlayerEquipsCache] = [final_equip] + all_equips
            return [
                cls(
                    e.equips_data,
                    e.talents_data,
                    e.kungfu_id,
                    e.global_role_id,
                    e.timestamp,
                    e.tag
                )
                for e in results
            ]
        return cls(
            final_equip.equips_data,
            final_equip.talents_data,
            final_equip.kungfu_id,
            final_equip.global_role_id,
            final_equip.timestamp,
            final_equip.tag
        )
                    

    def __init__(
            self,
            equips_lines: list,
            talents_lines: list[int],
            kungfu_id: int,
            global_role_id: int,
            timestamp: int = Time().raw_time,
            equip_tag: str = "",
            name: str = ""
        ):
        Equip.purge()
        self.equip_lines = equips_lines
        self.talents_lines = talents_lines
        self.kungfu_id = kungfu_id
        self.global_role_id = global_role_id
        self.timestamp = timestamp
        self.tag = equip_tag
        self.name = name

    @cached_property
    def equips(self) -> list[Equip]:
        results = []
        order = [4, 3, 8, 12, 10, 11, 5, 9, 6, 7, 2, 0, 1]
        priority = {val: i for i, val in enumerate(order)}
        sorted_lines = sorted(self.equip_lines, key=lambda obj: priority.get(int(obj[0]), len(order)))
        light_weapon: Equip | None = None
        for e in sorted_lines:
            if int(e[0]) != 1:
                instance = Equip(e)
                instance._pre_parse()
                instance.parse()
                instance._post_parse()
                if instance.location_index == 0:
                    light_weapon = instance
            else:
                instance = Equip(e)
                instance._pre_parse()
                if light_weapon is not None:
                    instance._color_stone_source = light_weapon._color_stone_source
                    instance._color_stone = light_weapon._color_stone
                    instance._diamonds = light_weapon._diamonds
                    instance._strength = light_weapon._strength
                instance.parse()
                instance._post_parse()
            results.append(instance)
        return results

    @cached_property
    def talents(self) -> list[Talent]:
        return [
            Talent(t)
            for t in self.talents_lines
        ]
    
    @cached_property
    def score(self):
        all_equips = self.equips
        if len(all_equips) < 13:
            return sum([e.score for e in all_equips])
        else:
            return sum([e.score for e in all_equips[:-2]]) + int((all_equips[-2].score + all_equips[-1].score) / 2)

    @cached_property
    def attributes(self) -> dict[str, str]:
        basic_attr = {}
        for each_equip in self.equips:
            basic_attr = merge_dicts(cast(dict[str, float], each_equip.attributes), basic_attr)
        for set_id, set_count in Equip.equip_sets.items():
            set_attr = TabCache.get_set(set_id, set_count)
            basic_attr = merge_dicts(basic_attr, set_attr)
        return FinalAttr(cast(dict[str, int], basic_attr), self.kungfu_id).output_attr()

    def save(self):
        pretags = {
            "PVE": 0,
            "PVP": 0,
            "PVX": 0
        }
        if self.tag == "":
            for e in self.equips:
                if "atDecriticalDamagePowerBase" in e.attributes:
                    pretags["PVP"] += 1
                if "atPVXAllRound" in e.attributes:
                    pretags["PVX"] += 1
                else:
                    pretags["PVE"] += 1
            self.tag = max(pretags, key=lambda k: pretags[k])
        exist_same_tag_equip = cast(PlayerEquipsCache | None, db.where_one(PlayerEquipsCache(), "global_role_id = ? AND tag = ? AND kungfu_id = ?", self.global_role_id, self.tag, self.kungfu_id, default=None))
        if exist_same_tag_equip is not None:
            exist_same_tag_equip.equips_data = self.equip_lines
            exist_same_tag_equip.global_role_id = self.global_role_id
            exist_same_tag_equip.kungfu_id = self.kungfu_id
            exist_same_tag_equip.timestamp = self.timestamp
            if exist_same_tag_equip.talents_data and self.talents and not (all([(t.name == "未知") for t in self.talents])):
                exist_same_tag_equip.talents_data = self.talents_lines
        else:
            exist_same_tag_equip = PlayerEquipsCache(
                equips_data = self.equip_lines,
                talents_data = self.talents_lines,
                global_role_id = self.global_role_id,
                kungfu_id = self.kungfu_id,
                tag = self.tag,
                timestamp = self.timestamp
            )
        db.save(exist_same_tag_equip)