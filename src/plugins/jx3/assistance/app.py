from typing import Union, Literal
from pathlib import Path

from src.constant.jx3 import school_name_aliases, skill_icons, color_list

from src.tools.basic.group import getGroupSettings, setGroupSettings
from src.tools.utils.time import get_current_time
from src.tools.utils.request import get_api
from src.tools.generate import generate, get_uuid
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.utils.file import read, write
from src.tools.config import Config

import random

class Assistance:
    def __init__(self):
        pass

    async def check_description(self, group: str, description: str):
        opening = getGroupSettings(group, "opening")
        if not isinstance(opening, list):
            return
        for i in opening:
            if i["description"] == description:
                return False
        return True

    async def create_group(self, group: str, description: str, creator: str):
        status = await self.check_description(group, description)
        if not status:
            return "开团失败，已经有相同的团队关键词！\n使用“团队列表”可查看本群目前正在进行的团队。"
        new = {
            "creator": creator,
            "applying": [],
            "member": [[], [], [], [], []],
            "create_time": get_current_time(),
            "description": description
        }
        opening = getGroupSettings(group, "opening")
        if not isinstance(opening, list):
            return
        opening.append(new)
        setGroupSettings(group, "opening", opening)
        return "开团成功，团员可通过以下命令进行预定：\n预定 <团队关键词> <ID> <职业>\n上述命令使用时请勿带尖括号，职业请使用准确些的词语，避免使用“长歌”，“万花”等模棱两可的职业字眼，也可以是“躺拍”“老板”等词语。\n特别注意：团长请给自己预定，否则预定总人数将为26人！"

    async def apply_for_place(self, group: str, description: str, id: str, job: str, applyer: str):
        status = await self.check_apply(group, description, id)
        if status:
            return "唔……您似乎已经申请过了，请不要重复申请哦~\n如需修改请先发送“取消申请 <团队关键词> <ID>”，随后重新申请！"
        if job in ["老板", "躺", "躺拍"]:
            job_ = "老板"
        else:
            job_: Union[str, Literal[False]] = school_name_aliases(job)
            if not job_:
                return f"唔……{Config.bot_basic.bot_name}暂时没办法识别您的职业，请检查一下呗？\n避免使用“长歌”“万花”“天策”等字眼，您可以使用“天策t”“奶咕”“qc”等准确些的词语方便理解哦~\n如果您使用的词语实在无法识别，请使用标准名称，例如“离经易道”。"
        job_icon = await self.get_icon(job_)
        new = {
            "id": id,
            "job": job_,
            "img": job_icon,
            "apply": applyer,
            "time": get_current_time()
        }
        stg = await self.storge(group, description, new)
        if stg is False:
            return "唔……该团队似乎已满，申请失败！"
        else:
            return "预定成功！"

    async def cancel_apply(self, group: str, description: str, id: str, actor: str):
        status = await self.check_apply(group, description, id)
        if status is False:
            return "唔……您似乎还没申请呢！"
        now = getGroupSettings(group, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == description or now.index(i) == description:
                for x in i["member"]:
                    for y in x:
                        if y["id"] == id:
                            if y["apply"] != actor and i["creator"] != actor:
                                return "请勿修改他人留坑！"
                            x.remove(y)
                            setGroupSettings(group, "opening", now)
                            return "成功取消留坑！"
        return "取消失败，未知错误。"

    async def dissolve(self, group: str, description: str, actor: str):
        now = getGroupSettings(group, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == description or now.index(i) == description:
                if i["creator"] != actor:
                    return "非创建者无法解散团队哦~"
                now.remove(i)
                setGroupSettings(group, "opening", now)
                return "解散团队成功！"

    async def storge(self, group: str, description: str, info: dict):
        now = getGroupSettings(group, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == description or now.index(i) == description:
                members = i["member"]
                for x in members:
                    if len(x) != 5:
                        x.append(info)
                        setGroupSettings(group, "opening", now)
                        return True
                    else:
                        continue
        return False

    async def get_icon(self, job: str):
        for i in skill_icons:
            if i["name"] == job:
                return i["data"]
        return False

    async def check_apply(self, group: str, description: str, id: str):
        file_content = getGroupSettings(group, "opening")
        if not isinstance(file_content, list):
            return
        for i in file_content:
            if i["description"] == description or file_content.index(i) == description:
                for x in i["member"]:
                    for y in x:
                        if y["id"] == id:
                            return True
        return False
    
    def job_to_type(self, job: str):
        if job in ["铁牢律", "明尊琉璃体", "洗髓经", "铁骨衣"]:
            return "T"
        elif job in ["离经易道", "补天诀", "相知", "灵素", "云裳心经"]:
            return "N"
        elif job == "老板":
            return "B"
        else:
            return "D"

    async def generate_html(self, group: str, description):
        now = getGroupSettings(group, "opening")
        if not isinstance(now, list):
            return
        for i in now:
            if i["description"] == description or now.index(i) == description:
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
                            count[self.job_to_type(a["job"])] += 1
                            img_src = a["img"]
                            job_color = color_list.get(a["job"], "#000000")  # 默认颜色为黑色
                            id_text = a["id"]
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
                bg = ASSETS + "/image/assistance/" + str(random.randint(1, 10)) + ".jpg"
                html_table += "</table>"
                font = ASSETS + "/font/custom.ttf"
                html = read(VIEWS + "/jx3/assistance/assistance.html").replace("$tablecontent", html_table).replace("$creator", str(creator)).replace("$tc", str(count["T"])).replace("$nc", str(count["N"])).replace("$bc", str(count["B"])).replace("$dc", str(count["D"])).replace("$customfont", font).replace("$rdbg", bg).replace("$title", description)
                final_html = CACHE + "/" + get_uuid() + ".html"
                write(final_html, html)
                final_path = await generate(final_html, False, ".background-container", False)
                if not isinstance(final_path, str):
                    return
                return Path(final_path).as_uri()
        return False