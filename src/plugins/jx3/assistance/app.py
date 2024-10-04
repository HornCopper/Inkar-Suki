from typing import Literal
from pathlib import Path

from src.config import Config
from src.const.jx3.kungfu import Kungfu
from src.const.path import (
    ASSETS,
    build_path
)
from src.utils.time import Time
from src.utils.generate import generate
from src.utils.database.operation import get_group_settings, set_group_settings

from src.templates import SimpleHTML

import random

class Assistance:
    def __init__(self):
        pass

    async def check_description(self, group_id: str, keyword: str) -> bool | None:
        opening = get_group_settings(group_id, "opening")
        if not isinstance(opening, list):
            return
        for i in opening:
            if i["description"] == keyword:
                return False
        return True

    async def create_group(self, group_id: str, keyword: str, creator_id: str) -> str | None:
        status = await self.check_description(group_id, keyword)
        if not status:
            return "开团失败，已经有相同的团队关键词！\n使用“团队列表”可查看本群目前正在进行的团队。"
        new = {
            "creator": creator_id,
            "applying": [],
            "member": [[], [], [], [], []],
            "create_time": Time().raw_time,
            "description": keyword
        }
        opening = get_group_settings(group_id, "opening")
        if not isinstance(opening, list):
            return
        opening.append(new)
        set_group_settings(group_id, "opening", opening)
        return "开团成功，团员可通过以下命令进行预定：\n预定 <团队关键词> <ID> <职业>\n上述命令使用时请勿带尖括号，职业请使用准确些的词语，避免使用“长歌”，“万花”等模棱两可的职业字眼，也可以是“躺拍”“老板”等词语。\n特别注意：团长请给自己预定，否则预定总人数将为26人！"

    async def apply_for_place(self, group_id: str, keyword: str, role_name: str, role_type: str, user_id: str) -> str:
        status = await self.check_apply(group_id, keyword, role_name)
        if status:
            return "唔……您似乎已经申请过了，请不要重复申请哦~\n如需修改请先发送“取消申请 <团队关键词> <ID>”，随后重新申请！"
        if role_type in ["老板", "躺", "躺拍"]:
            role_actual_type = "老板"
        else:
            role_actual_type: str | None = Kungfu(role_type).name
            if not role_actual_type:
                return f"唔……{Config.bot_basic.bot_name}暂时没办法识别您的职业，请检查一下呗？\n避免使用“长歌”“万花”“天策”等字眼，您可以使用“天策t”“奶咕”“qc”等准确些的词语方便理解哦~\n如果您使用的词语实在无法识别，请使用标准名称，例如“离经易道”。"
        job_icon = Kungfu(role_actual_type).icon if role_actual_type != "老板" else build_path(ASSETS, ["image", "jx3", "kungfu"], end_with_slash=True) + "老板.png"
        new = {
            "role": role_name,
            "role_type": role_actual_type,
            "img": job_icon,
            "apply": user_id,
            "time": Time().raw_time
        }
        stg = await self.storge(group_id, keyword, new)
        if stg is False:
            return "唔……该团队似乎已满，申请失败！"
        else:
            return "预定成功！"

    async def cancel_apply(self, group_id: str, keyword: str, role_name: str, user_id: str) -> str | None:
        status = await self.check_apply(group_id, keyword, role_name)
        if status is False:
            return "唔……您似乎还没申请呢！"
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == keyword or now.index(i) == keyword:
                for x in i["member"]:
                    for y in x:
                        if y["role"] == role_name:
                            if y["apply"] != user_id and i["creator"] != user_id:
                                return "请勿修改他人留坑！"
                            x.remove(y)
                            set_group_settings(group_id, "opening", now)
                            return "成功取消留坑！"
        return "取消失败，未知错误。"

    async def dissolve(self, group_id: str, keyword: str, user_id: str) -> str | None:
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == keyword or now.index(i) == keyword:
                if i["creator"] != user_id:
                    return "非创建者无法解散团队哦~"
                now.remove(i)
                set_group_settings(group_id, "opening", now)
                return "解散团队成功！"

    async def storge(self, group_id: str, keyword: str, content: dict) -> bool | None:
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == keyword or now.index(i) == keyword:
                members = i["member"]
                for x in members:
                    if len(x) != 5:
                        x.append(content)
                        set_group_settings(group_id, "opening", now)
                        return True
                    else:
                        continue
        return False

    async def check_apply(self, group_id: str, keyword: str, role_name: str) -> bool | None:
        file_content = get_group_settings(group_id, "opening")
        if not isinstance(file_content, list):
            return
        for i in file_content:
            if i["description"] == keyword or file_content.index(i) == keyword:
                for x in i["member"]:
                    for y in x:
                        if y["role"] == role_name:
                            return True
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

    async def generate_html(self, group_id: str, keyword: str) -> Literal[False] | str | None:
        now = get_group_settings(group_id, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == keyword or now.index(i) == keyword:
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
                bg = build_path(ASSETS, ["image", "assistance", str(random.randint(1, 10)) + ".jpg"])
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
                    title = keyword
                )
                final_path = await generate(str(html), ".background-container", False)
                if not isinstance(final_path, str):
                    return
                return Path(final_path).as_uri()
        return False