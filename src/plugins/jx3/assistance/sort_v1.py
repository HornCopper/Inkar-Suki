def rearrange_teams(input_teams: list[list[dict]]) -> list[list[dict]]: # actually list[list[dict | None]]
    # 心法类型定义
    phisical_core = ["凌海诀", "隐龙诀", "太虚剑意", "孤锋诀", "惊羽诀"]
    general_core = ["山海心诀"]
    magical_core = ["天罗诡道", "莫问", "紫霞功", "周天功", "花间游"]
    phisical = ["傲血战意", "分山劲", "太虚剑意", "惊羽诀", "问水诀", "笑尘诀", "北傲诀", "凌海诀", "隐龙诀", "孤锋诀", "山海心诀"]
    magical = ["冰心诀", "花间游", "毒经", "莫问", "无方", "易筋经", "焚影圣诀", "紫霞功", "天罗诡道", "太玄经", "周天功", "幽罗引"]
    all_cores = phisical_core + general_core + magical_core
    
    # 将input转换成一维列表，过滤掉空值
    all_members = [item for sublist in input_teams for item in sublist if item]
    original_count = len(all_members)
    columns = [[] for _ in range(5)]
    used_members = set()

    # 分类成员并统计数量
    core_members = []
    phisical_members = []
    magical_members = []
    other_members = []
    
    total_phisical = 0
    total_magical = 0

    # 第一次遍历：统计内外功总数
    for member in all_members:
        if member["role_type"] in phisical:
            total_phisical += 1
        elif member["role_type"] in magical:
            total_magical += 1

    # 第二次遍历：分类成员
    for member in all_members:
        if member["role_type"] in all_cores:
            core_members.append(member)
        elif member["role_type"] in phisical:
            phisical_members.append(member)
        elif member["role_type"] in magical:
            magical_members.append(member)
        else:
            other_members.append(member)

    # 按优先级排序阵眼成员
    core_members.sort(key=lambda x: all_cores.index(x["role_type"]) if x["role_type"] in all_cores else float("inf"))

    # 根据内外功比例分配阵眼数量
    max_columns = 5
    try:
        phisical_core_count = min(round(total_phisical / (total_phisical + total_magical) * max_columns), len([m for m in core_members if m["role_type"] in phisical_core]))
    except ZeroDivisionError:
        phisical_core_count = 0
    try:
        magical_core_count = min(max_columns - phisical_core_count, len([m for m in core_members if m["role_type"] in magical_core]))
    except ZeroDivisionError:
        magical_core_count = 0

    # 选择阵眼
    selected_cores = []
    phisical_core_selected = 0
    magical_core_selected = 0

    for core in core_members[:]:
        if core["role_type"] in phisical_core and phisical_core_selected < phisical_core_count:
            selected_cores.append(core)
            phisical_core_selected += 1
            core_members.remove(core)
        elif core["role_type"] in magical_core and magical_core_selected < magical_core_count:
            selected_cores.append(core)
            magical_core_selected += 1
            core_members.remove(core)

    total_used_members = 0

    # 分配选中的阵眼
    for col_idx, core in enumerate(selected_cores):
        columns[col_idx].append(core)
        used_members.add(core["role"])
        total_used_members += 1

    # 将未使用的阵眼成员加入到相应的普通成员池中
    for remaining_core in core_members:
        if remaining_core["role_type"] in phisical:
            phisical_members.append(remaining_core)
        elif remaining_core["role_type"] in magical:
            magical_members.append(remaining_core)

    # 填充剩余成员
    for col_idx in range(5):
        if len(columns[col_idx]) == 0:  # 没有阵眼的列
            # 根据当前内外功剩余数量决定该列类型
            if len(phisical_members) >= len(magical_members):
                preferred_list = phisical_members
            else:
                preferred_list = magical_members
        else:  # 有阵眼的列
            preferred_list = phisical_members if columns[col_idx][0]["role_type"] not in magical_core else magical_members

        # 填充当前列
        while len(columns[col_idx]) < 5:
            member_added = False
            if preferred_list:
                for member in preferred_list[:]:
                    if member["role"] not in used_members:
                        columns[col_idx].append(member)
                        used_members.add(member["role"])
                        total_used_members += 1
                        preferred_list.remove(member)
                        member_added = True
                        break
            
            if not member_added and other_members:
                for member in other_members[:]:
                    if member["role"] not in used_members:
                        columns[col_idx].append(member)
                        used_members.add(member["role"])
                        total_used_members += 1
                        other_members.remove(member)
                        member_added = True
                        break
            
            if not member_added:
                columns[col_idx].append({"role": None, "role_type": None})

    # 转置列为行
    output_teams = [[columns[j][i] for j in range(5)] for i in range(5)]

    # 兜底逻辑
    if total_used_members < original_count:
        output_teams = [row + [{"role": None, "role_type": None}] * (5 - len(row)) for row in input_teams]
        output_teams += [[{"role": None, "role_type": None}] * 5] * (5 - len(output_teams))

    return output_teams