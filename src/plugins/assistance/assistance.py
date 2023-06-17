import os
import time
import json

from tabulate import tabulate
from pathlib import Path
from random import randint

from src.tools.file import get_resource_path
from src.tools.file import read, write
from src.constant.jx3.skilldatalib import aliases as get_job_aliases, kftosh as get_xinfa_belong
from src.tools.config import Config
from src.tools.utils import get_api
from src.tools.generate import get_uuid

from . import DATA, skill_icons, TOOLS

CACHE = TOOLS[:-5] + "cache"

token = Config.jx3api_globaltoken

css = """
<style>
            ::-webkit-scrollbar 
            {
                display: none;   
            }
            table 
            { 
                border-collapse: collapse; 
            } 
            table, th, td
            { 
                border: 1px solid rgba(0,0,0,0.05); 
                font-size: 0.8125rem; 
                font-weight: 500; 
            } 
            th, td 
            { 
                padding: 15px; 
                text-align: left; 
            }
            @font-face
            {
                font-family: Custom;
                src: url("ctft");
            }
</style>"""
path = Path(get_resource_path(f'font{os.sep}fzht.ttf'))
css = css.replace("ctft", path.as_uri())


class Assistance:
    async def check_description(group: str, description: str):
        file_content = json.loads(read(f"{DATA}/{group}/opening.json"))
        for i in file_content:
            if i["description"] == description:
                return False
        return True

    async def create_group(group: str, description: str, creator: str):
        group_info = json.loads(read(f"{DATA}/{group}/jx3group.json"))
        server = group_info["server"]
        if group_info["server"] == "":
            return "开团失败，未绑定服务器的群聊暂无法使用该功能，请先联系群主或管理员进行绑定哦~"
        status = await Assistance.check_description(group, description)
        if status == False:
            return "开团失败，已经有相同的团队关键词！\n使用“团队列表”可查看本群目前正在进行的团队。"
        new = {
            "creator": creator,
            "applying": [],
            "member": [[], [], [], [], []],
            "create_time": int(time.time()),
            "description": description,
            "server": server
        }
        now = json.loads(read(f"{DATA}/{group}/opening.json"))
        now.append(new)
        write(f"{DATA}/{group}/opening.json",
              json.dumps(now, ensure_ascii=False))
        return "开团成功，团员可通过以下命令进行预定：\n预定 <团队关键词> <ID> <职业>\n上述命令使用时请勿带尖括号，职业请使用准确些的词语，避免使用“长歌”，“万花”等模棱两可的职业字眼，也可以是“躺拍”“老板”等词语。\n特别注意：团长请给自己预定，否则预定总人数将为26人！"

    async def apply_for_place(group: str, description: str, id: str, job: str, applyer: str):
        status = await Assistance.check_apply(group, description, id)
        if status:
            return "唔……您似乎已经申请过了，请不要重复申请哦~\n如需修改请先发送“取消申请 <团队关键词> <ID>”，随后重新申请！"
        group_info = json.loads(read(f"{DATA}/{group}/jx3group.json"))
        server = group_info["server"]
        if job in ["老板", "躺", "躺拍"]:
            job = "老板"
        else:
            job = get_job_aliases(job)
            if job == False:
                return "唔……音卡暂时没办法识别您的职业，请检查一下呗？\n避免使用“长歌”“万花”“天策”等字眼，您可以使用“天策t”“奶咕”“qc”等准确些的词语方便理解哦~\n如果您使用的词语实在无法识别，请使用标准名称，例如“离经易道”。"
        job_icon = await Assistance.get_icon(job)
        final_url = f"https://www.jx3api.com/data/role/roleInfo?token={token}&server={server}&name={id}"
        player_data = await get_api(final_url)
        try:
            uid = player_data["data"]["roleId"]
        except:
            return "无法获取到UID！"
        if job != "老板":
            if player_data["data"]["forceName"] != get_xinfa_belong(job):
                return "检测到自身预定职业和角色职业冲突，预定失败。"
        new = {
            "uid": uid,
            "id": id,
            "job": job,
            "img": job_icon,
            "apply": applyer,
            "time": int(time.time()),
            "server": server
        }
        stg = await Assistance.storge(group, description, new)
        if stg == False:
            return "唔……该团队似乎已满，申请失败！"
        else:
            return "预定成功！"

    async def cancel_apply(group: str, description: str, id: str, actor: str):
        status = await Assistance.check_apply(group, description, id)
        if status == False:
            return "唔……您似乎还没申请呢！"
        now = json.loads(read(f"{DATA}/{group}/opening.json"))
        for i in now:
            if i["description"] == description:
                for x in i["member"]:
                    for y in x:
                        if y["id"] == id:
                            if y["apply"] != actor:
                                return "请勿修改他人留坑！"
                            x.remove(y)
                            write(f"{DATA}/{group}/opening.json",
                                  json.dumps(now, ensure_ascii=False))
                            return "成功取消留坑！"
        return "取消失败，未知错误。"

    async def dissolve(group: str, description: str, actor: str):
        now = json.loads(read(f"{DATA}/{group}/opening.json"))
        for i in now:
            if i["description"] == description:
                if i["creator"] != actor:
                    return "非创建者无法解散团队哦~"
                now.remove(i)
                write(f"{DATA}/{group}/opening.json",
                      json.dumps(now, ensure_ascii=False))
                return "解散团队成功！"

    async def storge(group: str, description: str, info: dict):
        now = json.loads(read(f"{DATA}/{group}/opening.json"))
        for i in now:
            if i["description"] == description:
                members = i["member"]
                for x in members:
                    if len(x) != 5:
                        x.append(info)
                        write(f"{DATA}/{group}/opening.json",
                              json.dumps(now, ensure_ascii=False))
                        return True
                    else:
                        continue
        return False

    async def get_icon(job: str):
        for i in skill_icons:
            if i["name"] == job:
                return i["data"]
        return False

    async def check_apply(group: str, description: str, id: str):
        file_content = json.loads(read(f"{DATA}/{group}/opening.json"))
        for i in file_content:
            if i["description"] == description:
                for x in i["member"]:
                    for y in x:
                        if y["id"] == id:
                            return True
        return False

    async def time_convert(time1: int):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time1))

    async def generate_html(group: str, description: str):
        now = json.loads(read(f"{DATA}/{group}/opening.json"))
        for i in now:
            if i["description"] == description:
                chart = []
                creator = i["creator"]
                time_ = await Assistance.time_convert(i["create_time"])
                server = i["server"]
                lenth = len(i["member"][0]) + len(i["member"][1]) + \
                    len(i["member"][2]) + \
                    len(i["member"][3]) + len(i["member"][4])
                chart.append([f"创建者：{creator}", description,
                             time_, server, f"{lenth}/25"])
                for x in i["member"]:
                    space = []
                    for y in x:
                        icon = y["img"]
                        id = y["id"]
                        uid = y["uid"]
                        job = y["job"]
                        time1 = await Assistance.time_convert(y["time"])
                        content = f"<img src={icon} width=\"20\" height=\"20\"></img>{id}<br>职业：{job}<br>UID：{uid}<br>{time1}"
                        space.append(content)
                    chart.append(space)
                final_html = "<div style=\"font-family:Custom\">" + \
                    tabulate(chart, tablefmt="unsafehtml") + "</div>" + css
                path = CACHE + "/" + get_uuid() + ".html"
                write(path, final_html)
                return path
        return False

    async def random_member(group: str, description: str):
        now = json.loads(read(f"{DATA}/{group}/opening.json"))
        members = []
        for i in now:
            if i["description"] == description:
                for x in i["member"]:
                    for y in x:
                        members.append(y["id"])
        length = len(members)
        if length == 0:
            return "没有任何人可供抽取哦……"
        random_num = randint(0, length - 1)
        return "您抽中了：\n" + members[random_num]