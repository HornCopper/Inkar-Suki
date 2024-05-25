from src.tools.basic import *

from tabulate import tabulate

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
path = Path(get_resource_path(f"font{os.sep}custom.ttf"))
css = css.replace("ctft", path.as_uri())


class Assistance:
    async def check_description(group: str, description: str):
        file_content = json.loads(read(f"{DATA}/{group}/opening.json"))
        for i in file_content:
            if i["description"] == description:
                return False
        return True

    async def create_group(group: str, description: str, creator: str):
        status = await Assistance.check_description(group, description)
        if status == False:
            return "开团失败，已经有相同的团队关键词！\n使用“团队列表”可查看本群目前正在进行的团队。"
        new = {
            "creator": creator,
            "applying": [],
            "member": [[], [], [], [], []],
            "create_time": getCurrentTime(),
            "description": description
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
        if job in ["老板", "躺", "躺拍"]:
            job = "老板"
        else:
            job = aliases(job)
            if job is False:
                return f"唔……{Config.name}暂时没办法识别您的职业，请检查一下呗？\n避免使用“长歌”“万花”“天策”等字眼，您可以使用“天策t”“奶咕”“qc”等准确些的词语方便理解哦~\n如果您使用的词语实在无法识别，请使用标准名称，例如“离经易道”。"
        job_icon = await Assistance.get_icon(job)
        new = {
            "id": id,
            "job": job,
            "img": job_icon,
            "apply": applyer,
            "time": getCurrentTime()
        }
        stg = await Assistance.storge(group, description, new)
        if stg is False:
            return "唔……该团队似乎已满，申请失败！"
        else:
            return "预定成功！"

    async def cancel_apply(group: str, description: str, id: str, actor: str):
        status = await Assistance.check_apply(group, description, id)
        if status is False:
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
                write(f"{DATA}/{group}/opening.json", json.dumps(now, ensure_ascii=False))
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
    
    def job_to_type(job: str):
        if job in ["铁牢律", "明尊琉璃体", "洗髓经", "铁骨衣"]:
            return "T"
        elif job in ["离经易道", "补天诀", "相知", "灵素", "云裳心经"]:
            return "N"
        elif job == "老板":
            return "B"
        else:
            return "D"

    async def generate_html(group: str, description: str):
        now = json.loads(read(f"{DATA}/{group}/opening.json"))
        for i in now:
            if i["description"] == description:
                colorList = await get_api("https://inkar-suki.codethink.cn/schoolcolors")
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
                            count[Assistance.job_to_type(a["job"])] += 1
                            img_src = a["img"]
                            job_color = colorList.get(a["job"], "#000000")  # 默认颜色为黑色
                            id_text = a["id"]
                            qq_text = a["apply"]
                            cell_content = f"""
                            <div class="content-cell">
                                <img src={img_src}>
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
                bg = ASSETS + "/image/assistance/" + random.randint(1, 9) + ".jpg"
                html_table += "</table>"
                font = ASSETS + "/font/custom.ttf"
                html = read(VIEWS + "/jx3/assistance/assistance.html").replace("$tablecontent", html_table).replace("$creator", creator).replace("$tc", count["T"]).replace("$nc", count["N"]).replace("$bc", count["B"]).replace("$dc", count["D"]).replace("$customfont", font).replace("$rdbg", bg)
                final_html = CACHE + "/" + get_uuid() + ".html"
                write(final_html, html)
                final_path = await generate(final_html, False, "body", False)
                return Path(final_path).as_uri()
        return False