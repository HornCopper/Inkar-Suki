from typing import Literal
from pathlib import Path

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

import random
import re

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
        return "开团成功，团员可通过以下命令进行预定：\n预定 <团队关键词/序号> <ID> <职业>\n可使用“团队列表”查看该团队的序号！"

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
                return f"唔……{Config.bot_basic.bot_name}暂时没办法识别您的职业，请检查一下呗？"\
                    "\n避免使用“长歌”“万花”“天策”等字眼，您可以使用“天策t”“奶咕”“qc”等准确些的词语方便理解哦~"\
                    "\n如果您使用的词语实在无法识别，请使用标准名称，例如“离经易道”。"
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
        job_icon = Kungfu(role_actual_type).icon if role_actual_type != "老板" else build_path(ASSETS, ["image", "jx3", "kungfu"], end_with_slash=True) + "老板.png"
        new = {
            "role": role_name,
            "role_type": role_actual_type,
            "img": job_icon,
            "apply": user_id,
            "time": Time().raw_time
        }
        stg = self.storge(group_id, keyword, new)
        if stg is False:
            return "唔……该团队似乎已满，申请失败！"
        else:
            return "预定成功！"

    def cancel_apply(self, group_id: str, keyword: str, role_name: str, user_id: str) -> str | None:
        status = self.check_apply(group_id, keyword, role_name)
        if status is not True:
            return "唔……未找到该报名信息，或团队不存在！"
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == keyword or str(now.index(i) + 1) == keyword:
                for x in i["member"]:
                    for y in x:
                        if y["role"] == role_name:
                            if y["apply"] != user_id and i["creator"] != user_id:
                                return "请勿修改他人留坑！"
                            x.remove(y)
                            set_group_settings(group_id, "opening", now)
                            return "成功取消留坑！"
        raise ValueError("Please check the `assistance` app.py class `Assistance` method `cancel apply`!")

    def dissolve(self, group_id: str, keyword: str, user_id: str) -> str | None:
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == keyword or str(now.index(i) + 1) == keyword:
                if i["creator"] != user_id:
                    return "非创建者无法解散团队哦~"
                now.remove(i)
                set_group_settings(group_id, "opening", now)
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
            if str(each_team["creator"]) == str(creator) and (each_team["description"] == keyword or str(raw_teams.index(each_team) + 1) == keyword):
                goal_teams.append(each_team)
                set_group_settings(str(to_group), "opening", goal_teams)
                return True
        return False

    async def generate_html(self, group_id: str, keyword: str) -> Literal[False] | str | None:
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == keyword or str(now.index(i) + 1) == keyword:
                creator = i["creator"]
                count = {
                    "T": 0,
                    "N": 0,
                    "D": 0,
                    "B": 0
                }
                html_table = "<table>"
                for row in i["member"]:
                    html_table += "  <tr>\n"
                    for x in range(5):
                        if x < len(row) and row[x]:  # 如果索引在范围内且元素不为空
                            a = row[x]
                            count[self.role_type_abbr(a["role_type"])] += 1
                            img_src = a["img"]
                            job_color = Kungfu(a["role_type"]).color  # 默认颜色为白色
                            id_text = a["role"]
                            qq_text = a["apply"]
                            if id_text[0] == "#":
                                id_text = f"<s>{id_text}</s>"
                                qq_text = "<span style=\"color:gold\"><b>可报名此职业</b></span>"
                            cell_content = f"""
                            <div class="content-cell">
                                <img width="48px" height="48px" src={img_src}>
                                <p style="
                                    padding-left: 5px;
                                    color: {job_color};
                                    text-shadow:
                                        -1px -1px 0 #000, 
                                        1px -1px 0 #000, 
                                        -1px 1px 0 #000,
                                        1px 1px 0 #000;">
                                    {id_text}
                                    <br>（{qq_text}）
                                </p>
                            </div>
                            """
                        else:
                            cell_content = "<div class=\"content-cell\"></div>"
                        html_table += f"<td>{cell_content}</td>\n"
                    html_table += "</tr>\n"
                bg = build_path(ASSETS, ["image", "jx3", "assistance", str(random.randint(1, 10)) + ".jpg"])
                html_table += "</table>"
                font = build_path(ASSETS, ["font", "custom.ttf"])
                html = SimpleHTML(
                    "jx3",
                    "assistance",
                    table_content = html_table,
                    creator = creator,
                    T_count = str(count["T"]),
                    N_count = str(count["N"]),
                    D_count = str(count["D"]),
                    B_count = str(count["B"]),
                    font = font,
                    background = bg,
                    title = keyword if not check_number(keyword) else i["description"]
                )
                final_path = await generate(str(html), ".background-container", False)
                if not isinstance(final_path, str):
                    return
                return Path(final_path).as_uri()
        return False