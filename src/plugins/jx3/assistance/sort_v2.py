def rearrange_teams_new(input_teams: list[list[dict]]) -> list[list[dict]]:
    COL_A, COL_B, COL_C, COL_D, COL_E = range(5)
    MAX_ROWS = 5

    # 固定心法
    fixed_E = ["离经易道", "相知", "灵素", "补天诀", "云裳心经"]
    fixed_D = ["铁骨衣", "铁牢律", "明尊琉璃体", "洗髓经"]

    # 内外功
    physical = ["傲血战意", "分山劲", "太虚剑意", "惊羽诀", "问水诀", "笑尘诀", "北傲诀", "凌海诀", "隐龙诀", "孤锋诀", "山海心诀"]
    magical = ["冰心诀", "花间游", "毒经", "莫问", "无方", "易筋经", "焚影圣诀", "紫霞功", "天罗诡道", "太玄经", "周天功", "幽罗引"]

    members = [m for row in input_teams for m in row if m]

    columns = [[] for _ in range(5)]

    def try_put(col_idx: int, member: dict) -> bool:
        if len(columns[col_idx]) < MAX_ROWS:
            columns[col_idx].append(member)
            return True
        return False

    # 先分类
    bosses = []
    normal_members = []

    for m in members:
        if m["role_type"] == "老板":
            bosses.append(m)
        else:
            normal_members.append(m)

    normal_members.sort(key=lambda x: x["role_type"] not in (fixed_D + fixed_E))

    # 第一轮：非老板
    for m in normal_members:
        rt = m["role_type"]

        # 固定列优先
        if rt in fixed_E:
            if try_put(COL_E, m):
                continue
        if rt in fixed_D:
            if try_put(COL_D, m):
                continue

        if rt in magical:
            if try_put(COL_A, m):
                continue
            if try_put(COL_B, m):
                continue
            if try_put(COL_C, m):
                continue
            if try_put(COL_D, m):
                continue
            try_put(COL_E, m)
            continue

        if rt in physical:
            if try_put(COL_C, m):
                continue
            if try_put(COL_B, m):
                continue
            if try_put(COL_A, m):
                continue
            if try_put(COL_D, m):
                continue
            try_put(COL_E, m)
            continue


        # 兜底：直接塞 D
        try_put(COL_D, m)

    # 第二轮：老板（最低优先级）
    for m in bosses:
        placed = False
        for col in (COL_A, COL_B, COL_C):
            if try_put(col, m):
                placed = True
                break
        if placed:
            continue
        if try_put(COL_D, m):
            continue
        try_put(COL_E, m)

    # 补空位
    for col in columns:
        while len(col) < MAX_ROWS:
            col.append({"role": None, "role_type": None})

    # 列转行
    return [[columns[c][r] for c in range(5)] for r in range(5)]
