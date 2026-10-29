EQUIP_LOCATION = {
    "武器": 0,
    "重剑": 1,
    "暗器": 2,
    "上衣": 3,
    "帽子": 4,
    "项链": 5,
    "戒指1": 6,
    "戒指2": 7,
    "腰带": 8,
    "腰坠": 9,
    "下装": 10,
    "鞋子": 11,
    "护腕": 12,
}

def replace_enchant_in_equip_lines(
    equip_lines: list,
    location_code: int,
    enchant_id: int,
    *,
    is_color_stone: bool = False,
    is_common: bool = False,
) -> list:
    """Return a copy with only the requested enchant field changed."""
    import copy

    updated_lines = copy.deepcopy(equip_lines)
    target = next(
        (line for line in updated_lines if int(line[0]) == location_code),
        None,
    )
    if target is None:
        raise ValueError(f"equipment location {location_code} does not exist")

    if is_color_stone:
        if len(target) <= 4 or len(target[4]) <= 3 or len(target[4][3]) <= 1:
            raise ValueError("color stone slot is missing from equipment data")
        target[4][3][1] = enchant_id
    elif is_common:
        if len(target) <= 6:
            raise ValueError("common enchant slot is missing from equipment data")
        target[6] = enchant_id
    else:
        if len(target) <= 5:
            raise ValueError("permanent enchant slot is missing from equipment data")
        target[5] = enchant_id

    return updated_lines
