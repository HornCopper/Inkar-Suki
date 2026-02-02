from typing import Literal, overload
from datetime import datetime
from jinja2 import Template

from nonebot.adapters.onebot.v11 import MessageSegment as ms

from src.config import Config
from src.const.jx3.kungfu import Kungfu
from src.const.path import (
    ASSETS,
    build_path
)
from src.utils.analyze import check_number
from src.utils.time import Time
from src.utils.generate import generate
from src.utils.database.operation import get_group_settings, set_group_settings

from src.templates import SimpleHTML

from ._template import template_assistance_unit
from .sort_v1 import rearrange_teams as sort_teams_v1
from .sort_v2 import rearrange_teams_new as sort_teams_v2

import re

def to_transparent_hex(rgb_hex: str, alpha: int = 0x22) -> str:
    rgb_hex = rgb_hex.lstrip("#")
    return f"#{rgb_hex}{alpha:02X}"

def parse_limit(s: str) -> dict[str, int] | Literal[False]:
    pattern = r"([0-1]?[0-9]|2[0-5])([TNBD])"
    matches = re.findall(pattern, s)
    if len(matches) == 0 or len(matches) > 4:
        return False
    result = {key: 25 for key in "TNBD"}
    for value, key in matches:
        result[key] = int(value)
    return result

class Assistance:
    def __init__(self):
        pass

    def stastic_roles(self, nested_list: list[list[dict[str, str]]]) -> dict[str, int]:
        result = {"T": 0, "N": 0, "B": 0, "D": 0}
        for inner_list in nested_list:
            for item in inner_list:
                if "role_type" in item and item["role"][0] != "#":
                    role_type = self.role_type_abbr(item["role_type"])
                    if role_type in result:
                        result[role_type] += 1
        return result

    def check_description(self, group_id: str, keyword: str) -> bool | None:
        opening = get_group_settings(group_id, "opening")
        if not isinstance(opening, list):
            return
        for i in opening:
            if i["description"] == keyword or str(opening.index(i) + 1) == keyword:
                return False
        return True
    
    def get_kungfu_icon(self, kungfu_name: str) -> str:
        if kungfu_name != "老板":
            return Kungfu(kungfu_name).icon
        return build_path(ASSETS, ["image", "jx3", "kungfu"], end_with_slash=True) + "老板.png"

    def create_group(self, group_id: str, keyword: str, creator_id: str, /, limit: str = "") -> str | None:
        status = self.check_description(group_id, keyword)
        if not status:
            return "开团失败，已经有相同的团队关键词！\n使用“团队列表”可查看本群目前正在进行的团队。"
        new = {
            "creator": creator_id,
            "applying": [],
            "member": [[], [], [], [], []],
            "create_time": Time().raw_time,
            "description": keyword,
            "limit": limit
        }
        opening = get_group_settings(group_id, "opening")
        if not isinstance(opening, list):
            return
        opening.append(new)
        set_group_settings(group_id, "opening", opening)
        return "开团成功，团员可通过以下命令进行报名：\n报名 <团队关键词/序号> <职业> <ID>\n可使用“团队列表”查看该团队的序号！"

    def apply_for_place(self, group_id: str, keyword: str, role_name: str, role_type: str, user_id: str) -> str:
        if role_name == "#":
            return "请不要以单个井号创建预留位，可在井号后追加任意文字！"
        status = self.check_apply(group_id, keyword, role_name)
        if status is True:
            return "唔……您似乎已经申请过了，请不要重复申请哦~\n如需修改请先发送“取消申请 <团队关键词> <ID>”，随后重新申请！"
        if status is False:
            return "未找到对应团队！请检查后重试！"
        applyable = False
        if role_type in ["老板", "躺", "躺拍"]:
            role_actual_type = "老板"
        else:
            role_actual_type: str | None = Kungfu(role_type).name
            if role_actual_type is None:
                return "报名失败！请参考格式：\n报名 关键词/序号 职业 ID\n目前您可能是将最后两个参数写反导致无法识别职业，可参考命令格式后重试！"
        if role_name[0] == "#" and user_id != status["creator"]:
            return "只有团长才可创建预留职业位，请联系团长！"
        if "limit" not in status:
            applyable = True
        else:
            limit = status["limit"]
            parsed_limit = parse_limit(limit)
            if not parsed_limit:
                applyable = True
            else:
                if self.stastic_roles(status["member"]).get(self.role_type_abbr(role_actual_type), 0) < parsed_limit.get(self.role_type_abbr(role_actual_type), 0):
                    applyable = True
        if not applyable:
            return "您所申请或预留的职业类型已达到团长限制的最大数量，您可以更换其他职业参与本次团队活动！\n可使用“团队列表”查看该团队的职业人数限制！\n可使用“查看团队”查看该团队目前报名情况！"
        new = {
            "role": role_name,
            "role_type": role_actual_type,
            "apply": user_id,
            "time": Time().raw_time
        }
        storge_status = self.storge(group_id, keyword, new)
        if not storge_status:
            return "唔……该团队似乎已满，申请失败！"
        else:
            return "报名成功！"

    def cancel_apply(self, group_id: str, keyword: str, role_name: str, user_id: str) -> str | None:
        status = self.check_apply(group_id, keyword, role_name)
        if status is not True and not (isinstance(status, dict) and role_name[0] == "#"):
            return "唔……未找到该报名信息，或团队不存在！"
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return
        cancelled = False
        for i in now:
            if i["description"] == keyword or str(now.index(i) + 1) == keyword:
                for x in i["member"]:
                    for y in x:
                        if y["role"] == role_name:
                            if y["apply"] != user_id and i["creator"] != user_id:
                                return "请勿修改他人留坑！"
                            x.remove(y)
                            set_group_settings(group_id, "opening", now)
                            cancelled = True
                            return "成功取消留坑！"
        if not cancelled:
            raise ValueError("Please check the `assistance` app.py class `Assistance` method `cancel apply`!")

    def dissolve(self, group_id: str, keyword: str, user_id: str, is_admin: bool, dissolve_all: bool = False) -> str | None:
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return None

        targets = []
        for idx, item in enumerate(now):
            if dissolve_all:
                targets.append(item)
            elif item["description"] == keyword:
                targets.append(item)
            elif str(idx + 1) == keyword:
                targets.append(item)

        if not targets:
            return None

        for item in targets:
            if item["creator"] != user_id and not is_admin:
                return "非创建者无法解散团队！"

        new_now = [item for item in now if item not in targets]
        set_group_settings(group_id, "opening", new_now)

        return "解散团队成功！"

    def storge(self, group_id: str, keyword: str, content: dict) -> bool | None:
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == keyword or str(now.index(i) + 1) == keyword:
                members = i["member"]
                replaced = False
                for x in members:
                    for item in x:
                        if item["role"][0] == "#" and item["role_type"] == content["role_type"]:
                            x[x.index(item)] = content
                            replaced = True
                            set_group_settings(group_id, "opening", now)
                            return True
                if not replaced:
                    for x in members:
                        if len(x) < 5:
                            x.append(content)
                            set_group_settings(group_id, "opening", now)
                            return True
        return False

    def check_apply(self, group_id: str, keyword: str, role_name: str) -> bool | dict:
        """
        Returns:
            (True): User has applied the team.
            (False): Team not found.
            (type(dict)): Team found, but user has not applied.
        """
        file_content: list[dict] = get_group_settings(group_id, "opening")
        for i in file_content:
            if i["description"] == keyword or str(file_content.index(i) + 1) == keyword:
                if role_name[0] == "#":
                    return i
                for x in i["member"]:
                    for y in x:
                        if y["role"] == role_name:
                            return True
                return i
        return False
    
    def role_type_abbr(self, role_type: str) -> str:
        if role_type in ["铁牢律", "明尊琉璃体", "洗髓经", "铁骨衣"]:
            return "T"
        elif role_type in ["离经易道", "补天诀", "相知", "灵素", "云裳心经"]:
            return "N"
        elif role_type == "老板":
            return "B"
        else:
            return "D"
        
    def share_team(self, from_group: int, to_group: int, keyword: str, creator: int) -> bool:
        if self.check_description(str(from_group), keyword) or not self.check_description(str(to_group), keyword):
            return False
        raw_teams: list[dict] = get_group_settings(str(from_group), "opening")
        goal_teams: list[dict] = get_group_settings(str(to_group), "opening")
        for each_team in raw_teams:
            if (str(each_team["creator"]) == str(creator) or str(creator) in Config.bot_basic.bot_owner) and (each_team["description"] == keyword or str(raw_teams.index(each_team) + 1) == keyword):
                goal_teams.append(each_team)
                set_group_settings(str(to_group), "opening", goal_teams)
                return True
        return False
    
    @overload
    async def generate_html(self, group_id: str, keyword: str, new_sort_method: bool = False, all: Literal[False] = False) -> str | ms: ...

    @overload
    async def generate_html(self, group_id: str, keyword: str, new_sort_method: bool = False, all: Literal[True] = True) -> list[ms]: ...

    async def generate_html(self, group_id: str, keyword: str, new_sort_method: bool = False, all: bool = False) -> str | ms | list[ms]:
        if new_sort_method:
            method = sort_teams_v2
        else:
            method = sort_teams_v1
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return "数据异常，请先重置音卡！"
        images = []
        for i in now:
            if (i["description"] == keyword or str(now.index(i) + 1) == keyword) or all:
                creator = i["creator"]
                count = {
                    "T": 0,
                    "N": 0,
                    "D": 0,
                    "B": 0
                }
                html_table = "<table>"
                sorted_team = method(i["member"])
                html_table = []
                for row in sorted_team:
                    for x in range(5):
                        if x < len(row) and row[x]:  # 如果索引在范围内且元素不为空
                            a = row[x]
                            if a["role_type"] is None:
                                cell_content = "<div class=\"cell\"></div>"
                                html_table.append(cell_content)
                                continue
                            count[self.role_type_abbr(a["role_type"])] += 1
                            # icon = a["img"]
                            icon = self.get_kungfu_icon(a["role_type"])
                            color = Kungfu(a["role_type"]).color  # 默认颜色为白色
                            name = a["role"]
                            qq = a["apply"]
                            if name[0] == "#":
                                name = f"<s>{name}</s>"
                                qq = "<span style=\"color:gold\"><b>可报名此职业</b></span>"
                            cell_content = Template(template_assistance_unit).render(
                                color = to_transparent_hex(color),
                                icon = icon,
                                name = name,
                                qq = qq
                            )
                        else:
                            cell_content = "<div class=\"cell\"></div>"
                        html_table.append(cell_content)
                # bg = build_path(ASSETS, ["image", "jx3", "assistance", str(random.randint(1, 10)) + ".jpg"])
                font = build_path(ASSETS, ["font", "PingFangSC-Medium.otf"])
                html = SimpleHTML(
                    "jx3",
                    "assistance",
                    table_content = "\n".join(html_table),
                    creator = creator,
                    T_count = str(count["T"]),
                    N_count = str(count["N"]),
                    D_count = str(count["D"]),
                    B_count = str(count["B"]),
                    font = font,
                    # background = bg,
                    title = i["description"]
                )
                image = await generate(str(html), ".container", segment=True, viewport={"width": 1366, "height": 768})
                images.append(image)
        if images == []:
            return "未找到相关团队！"
        else:
            return images
    

def get_yzk_answer() -> str:
    time_table = {
        "00:00:00": "东-9,南-0,西-1,北-9",
        "00:15:00": "东-9,南-0,西-1,北-0",
        "00:30:00": "东-9,南-0,西-1,北-1",
        "00:45:00": "东-9,南-0,西-1,北-2",
        "01:00:00": "东-9,南-0,西-1,北-4",
        "01:15:00": "东-9,南-0,西-1,北-4",
        "01:30:00": "东-9,南-0,西-1,北-4",
        "01:45:00": "东-9,南-0,西-1,北-4",
        "02:00:00": "东-9,南-0,西-1,北-4",
        "02:15:00": "东-9,南-0,西-1,北-4",
        "02:30:00": "东-9,南-0,西-1,北-4",
        "02:45:00": "东-9,南-0,西-1,北-4",
        "03:00:00": "东-9,南-0,西-1,北-3",
        "03:15:00": "东-9,南-0,西-1,北-2",
        "03:30:00": "东-9,南-0,西-1,北-1",
        "03:45:00": "东-9,南-0,西-1,北-0",
        "04:00:00": "东-9,南-0,西-1,北-9",
        "04:15:00": "东-9,南-0,西-1,北-8",
        "04:30:00": "东-9,南-0,西-1,北-7",
        "04:45:00": "东-9,南-0,西-1,北-6",
        "05:00:00": "南-0,西-1,北-4,东-0",
        "05:15:00": "南-0,西-1,北-4,东-1",
        "05:30:00": "南-0,西-1,北-4,东-2",
        "05:45:00": "南-0,西-1,北-4,东-3",
        "06:00:00": "南-0,西-1,北-4,东-4",
        "06:15:00": "南-0,西-1,北-4,东-5",
        "06:30:00": "南-0,西-1,北-4,东-6",
        "06:45:00": "南-0,西-1,北-4,东-7",
        "07:00:00": "南-0,西-1,北-4,东-8",
        "07:15:00": "南-0,西-1,北-4,东-9",
        "07:30:00": "南-0,西-1,北-4,东-9",
        "07:45:00": "南-0,西-1,北-4,东-9",
        "08:00:00": "南-0,西-1,北-4,东-9",
        "08:15:00": "南-0,西-1,北-4,东-9",
        "08:30:00": "南-0,西-1,北-4,东-9",
        "08:45:00": "南-0,西-1,北-4,东-9",
        "09:00:00": "南-0,西-1,北-4,东-8",
        "09:15:00": "南-0,西-1,北-4,东-7",
        "09:30:00": "南-0,西-1,北-4,东-6",
        "09:45:00": "南-0,西-1,北-4,东-5",
        "10:00:00": "南-0,西-1,北-4,东-4",
        "10:15:00": "南-0,西-1,北-4,东-3",
        "10:30:00": "南-0,西-1,北-4,东-2",
        "10:45:00": "南-0,西-1,北-4,东-1",
        "11:00:00": "东-9,西-1,北-4,南-1",
        "11:15:00": "东-9,西-1,北-4,南-2",
        "11:30:00": "东-9,西-1,北-4,南-3",
        "11:45:00": "东-9,西-1,北-4,南-4",
        "12:00:00": "东-9,西-1,北-4,南-5",
        "12:15:00": "东-9,西-1,北-4,南-6",
        "12:30:00": "东-9,西-1,北-4,南-7",
        "12:45:00": "东-9,西-1,北-4,南-8",
        "13:00:00": "东-9,西-1,北-4,南-0",
        "13:15:00": "东-9,西-1,北-4,南-0",
        "13:30:00": "东-9,西-1,北-4,南-0",
        "13:45:00": "东-9,西-1,北-4,南-0",
        "14:00:00": "东-9,西-1,北-4,南-0",
        "14:15:00": "东-9,西-1,北-4,南-0",
        "14:30:00": "东-9,西-1,北-4,南-0",
        "14:45:00": "东-9,西-1,北-4,南-0",
        "15:00:00": "东-9,西-1,北-4,南-9",
        "15:15:00": "东-9,西-1,北-4,南-8",
        "15:30:00": "东-9,西-1,北-4,南-7",
        "15:45:00": "东-9,西-1,北-4,南-6",
        "16:00:00": "东-9,西-1,北-4,南-5",
        "16:15:00": "东-9,西-1,北-4,南-4",
        "16:30:00": "东-9,西-1,北-4,南-3",
        "16:45:00": "东-9,西-1,北-4,南-2",
        "17:00:00": "东-9,南-0,北-4,西-2",
        "17:15:00": "东-9,南-0,北-4,西-3",
        "17:30:00": "东-9,南-0,北-4,西-4",
        "17:45:00": "东-9,南-0,北-4,西-5",
        "18:00:00": "东-9,南-0,北-4,西-6",
        "18:15:00": "东-9,南-0,北-4,西-7",
        "18:30:00": "东-9,南-0,北-4,西-8",
        "18:45:00": "东-9,南-0,北-4,西-9",
        "19:00:00": "东-9,南-0,北-4,西-1",
        "19:15:00": "东-9,南-0,北-4,西-1",
        "19:30:00": "东-9,南-0,北-4,西-1",
        "19:45:00": "东-9,南-0,北-4,西-1",
        "20:00:00": "东-9,南-0,北-4,西-1",
        "20:15:00": "东-9,南-0,北-4,西-1",
        "20:30:00": "东-9,南-0,北-4,西-1",
        "20:45:00": "东-9,南-0,北-4,西-1",
        "21:00:00": "东-9,南-0,北-4,西-0",
        "21:15:00": "东-9,南-0,北-4,西-9",
        "21:30:00": "东-9,南-0,北-4,西-8",
        "21:45:00": "东-9,南-0,北-4,西-7",
        "22:00:00": "东-9,南-0,北-4,西-6",
        "22:15:00": "东-9,南-0,北-4,西-5",
        "22:30:00": "东-9,南-0,北-4,西-4",
        "22:45:00": "东-9,南-0,北-4,西-3",
        "23:00:00": "东-9,南-0,西-1,北-5",
        "23:15:00": "东-9,南-0,西-1,北-6",
        "23:30:00": "东-9,南-0,西-1,北-7",
        "23:45:00": "东-9,南-0,西-1,北-8"
    }
    now = datetime.now()
    hours = now.strftime("%H")
    minutes = now.strftime("%M")
    quarter = (int(minutes) // 15) * 15
    time_key = f"{hours}:{str(quarter).zfill(2)}:00"
    result = time_table.get(time_key, "无匹配结果")
    time_key_index = list(time_table.keys()).index(time_key)
    if time_key_index == len(time_table.keys()) - 1:
        next_result = time_table.get(list(time_table.keys())[0], "")
    else:
        next_result = time_table.get(list(time_table.keys())[time_key_index + 1], "")
    fixed_order = ["东", "南", "西", "北"]
    data = {item.split("-")[0]: item.split("-")[1] for item in result.split(",")}
    next_data = {item.split("-")[0]: item.split("-")[1] for item in next_result.split(",")}
    result = ",".join([f"{direction}-{data[direction]}" for direction in fixed_order])
    next_result = ",".join([f"{direction}-{next_data[direction]}" for direction in fixed_order])
    return f"当前时间: {time_key}\n结果: {result}\n下一结果：{next_result}"

def get_gyc_answer(points: str) -> tuple[list[str], int] | None:
    if len(points) != 4 or not points.isdigit():
        return None

    circle = [1, 2, 3, 4, 5, 6, 7, 8]
    nums = [int(c) for c in points]

    if len(set(nums)) != 4 or any(n not in circle for n in nums):
        return None

    remaining = [n for n in circle if n not in nums]

    options = {}
    for n in nums:
        idx = circle.index(n)
        entries = []
        for step, cw in [(1, False), (-1, True), (2, False), (-2, True)]:
            x = circle[(idx + step) % 8]
            if x in remaining:
                dist = abs(step) // 2
                entries.append((dist, cw, x))
        entries.sort(key=lambda x: (x[0], x[1]))
        options[n] = [e[2] for e in entries]

    assign = {}
    used = set()
    stack = []

    i = 0

    while True:
        if i == 4:
            break

        cur = nums[i]
        if not options[cur]:
            return None

        if len(stack) <= i:
            stack.append([0])

        cand_index = stack[i][0]

        if cand_index >= len(options[cur]):
            stack.pop()
            if i == 0:
                return None

            i -= 1
            prev_num = nums[i]
            used.remove(assign[prev_num])
            del assign[prev_num]
            stack[i][0] += 1
            continue

        cand = options[cur][cand_index]
        if cand not in used:
            assign[cur] = cand
            used.add(cand)
            i += 1
            continue
        else:
            stack[i][0] += 1

    pairs = [f"{n}{assign[n]}" for n in nums]
    safety = ((nums[0] + 3) % 8) + 1
    return pairs, safety