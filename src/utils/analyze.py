from typing import Any

Locations = [
    "武器", None, "暗器", "上衣", "帽子", "项链", "戒指", "戒指", "腰带", "腰坠", "下装", "鞋子", "护腕"
]

import re

def invert_dict(d: dict[str, str]) -> dict[str, str]:
    """
    将字典的键值对互换位置。

    Args:
        d (dict[str, str]): 需要键值互换的字典。
    """
    return {v: k for k, v in d.items()}

def sort_dict_list(dict_list: list[dict], key_name: str) ->list[dict]:
    """
    将`list[dict]`类型的变量，按`dict`的共有`key`的`value`进行排序。

    默认为从低到高，如需反过来请对结果进行`[::-1]`！

    Args:
        dict_list (list[dict]): 传入的字典列表。
        key_name (str): 排序依据`key`。
    """
    sorted_list = sorted(dict_list, key=lambda x: x[key_name])
    return sorted_list

def merge_dict_lists(list1: list[dict], list2: list[dict]) -> list[dict]:
    """
    将两个所有包含的`dict`的`key`均相同的`list[dict]`进行合并。

    `list2`的优先级高于`list1`，同时包含数据的时候，`list2`优先。

    Args:
        list1 (list[dict]): 需要合并的第一个字典列表。
        list2 (list[dict]): 需要合并的第二个字典列表。 
    """
    name_to_dict = {d["name"]: d for d in list1}
    for d in list2:
        if d["name"] in name_to_dict:
            name_to_dict[d["name"]]["time"] = d["time"]
        else:
            list1.append(d)
    return list1


def check_number(value: str | int) -> bool:
    """
    检查参数是否可以被转为数字。

    Args:
        value (str, int): 需要检查的变量。

    Returns:
        is_num (bool): 是否为数字。
    """
    if value is None:
        return False
    if isinstance(value, str):
        pattern = r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$"
        return bool(re.match(pattern, value))
    if isinstance(value, int):
        return True
    return value.isdecimal()

def extract_numbers(string: str) -> list[int]:
    """
    从字符串中提取数字。

    Args:
        string (str): 源字符串。

    Returns:
        number (list[int]): 字符串包含的数字。
    """
    pattern = r"\d+"
    numbers = re.findall(pattern, string)
    return [int(num) for num in numbers]

def merge_dicts(dict1: dict[str, float], dict2: dict[str, float]) -> dict[str, float]:
    """
    合并`dict[str, float]`。
    
    如果含有相同`Key`则求和放入新字典中。

    Args:
        dict1 (dict[str, float]): 第一个字典。
        dict2 (dict[str, float]): 第二个字典。

    Returns:
        result (dict[str, float]): 合并的字典。
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result:
            result[key] += value
        else:
            result[key] = value
    return result

def match(obj, **kwargs):
    return all(getattr(obj, k, None) == v for k, v in kwargs.items())

class TuilanData:
    def __init__(self, tuilan_data: dict[str, Any]):
        self.tuilan_data = tuilan_data

    def unit_parse(self, equip_data: dict) -> list[int]:
        equip_type = equip_data["EquipType"]["SubType"]
        location_id = Locations.index(equip_type)
        index_type = int(equip_data["TabType"])
        index_id = int(equip_data["ID"])
        strength = int(equip_data["StrengthLevel"])
        fivestones = []
        for each_fivestone in equip_data.get("FiveStone", []):
            fivestone_data = [5, int(each_fivestone["Level"]) + 24441]
            fivestones.append(fivestone_data)
        if location_id == 0:
            if "ColorStone" in equip_data:
                fivestones.append(
                    [0, int(equip_data["ColorStone"]["ID"])]
                )
        p_enchant = 0
        c_enchant = 0
        if "WPermanentEnchant" in equip_data:
            p_enchant = int(equip_data["WPermanentEnchant"]["ID"])
        if "WCommonEnchant" in equip_data:
            c_enchant = int(equip_data["WCommonEnchant"]["ID"])
        final_data = [
            location_id,
            index_type,
            index_id,
            strength,
            fivestones,
            p_enchant,
            c_enchant,
            0
        ]
        return final_data

    def output_jcl_line(self):
        final_equip_data: list = []
        for each_equip in self.tuilan_data["data"]["Equips"]:
            equip_data = self.unit_parse(each_equip)
            final_equip_data.append(equip_data)
        return final_equip_data