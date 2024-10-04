from typing import Dict, List

import re

def invert_dict(d: Dict[str, str]) -> Dict[str, str]:
    """
    将字典的键值对互换位置。

    Args:
        d (Dict[str, str]): 需要键值互换的字典。
    """
    return {v: k for k, v in d.items()}

def sort_dict_list(dict_list: List[dict], key_name: str) ->List[dict]:
    """
    将`List[dict]`类型的变量，按`dict`的共有`key`的`value`进行排序。

    Args:
        dict_list (List[dict]): 传入的字典列表。
        key_name (str): 排序依据`key`。
    """
    sorted_list = sorted(dict_list, key=lambda x: x[key_name])
    return sorted_list

def merge_dict_lists(list1: List[dict], list2: List[dict]) -> List[dict]:
    """
    将两个所有包含的`dict`的`key`均相同的`List[dict]`进行合并。

    `list2`的优先级高于`list1`，同时包含数据的时候，`list2`优先。

    Args:
        list1 (List[dict]): 需要合并的第一个字典列表。
        list2 (List[dict]): 需要合并的第二个字典列表。 
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

def extract_numbers(string: str) -> List[int]:
    """
    从字符串中提取数字。

    Args:
        string (str): 源字符串。

    Returns:
        number (List[int]): 字符串包含的数字。
    """
    pattern = r"\d+"
    numbers = re.findall(pattern, string)
    return [int(num) for num in numbers]