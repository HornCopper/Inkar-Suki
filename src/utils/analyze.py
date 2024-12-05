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
