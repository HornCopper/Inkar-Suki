from pathlib import Path
from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, build_path
from src.utils.decorators import token_required
from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import template_interserver, template_local, table_recruit_head

async def check_ad(msg: str, data: dict) -> bool:
    data = data["data"]
    for x in data:
        status = []
        for num in range(len(x)):
            status.append(True)
        result = []
        for y in x:
            if msg.find(y) != -1:
                result.append(True)
            else:
                result.append(False)
        if status == result:
            return True
    return False

@token_required
async def get_recruit_image(server: str, keyword: str = "", local: bool = False, filter: bool = False, token: str = ""):
    final_url = f"{Config.jx3.api.url}/data/member/recruit?token={token}&server={server}"
    data = (await Request(final_url).get()).json()
    if data["code"] != 200:
        return ["唔……未找到相关团队，请检查后重试！"]
    adFlags = (await Request("https://inkar-suki.codethink.cn/filters").get()).json()
    time_now = Time(data["data"]["time"]).format("%H:%M:%S")
    data = data["data"]["data"]
    contents = []
    for i in range(len(data)):
        detail = data[i]
        content = detail["content"]
        if filter:
            to_filter = await check_ad(content, adFlags)
            if to_filter:
                continue
        flag = False if not detail["roomID"] else True
        if local and flag:
            continue
        flag = "" if not detail["roomID"] else "<img src=\"https://img.jx3box.com/image/box/servers.svg\" style=\"width:20px;height:20px;\">" 
        num = str(i + 1)
        name = detail["activity"]
        level = str(detail["level"])
        leader = detail["leader"]
        count = str(detail["number"]) + "/" + str(detail["maxNumber"])
        create_time = Time(detail["createTime"]).format()
        if local:
            template = template_local
            flag = ""
        else:
            template = template_interserver
        contents.append(
            Template(template).render(
                sort = num,
                name = name,
                level = level,
                leader = leader,
                count = count,
                content = content,
                time = create_time,
                flag = flag
            )
        )
        if len(contents) == 50:
            break
    html = str(
        HTMLSourceCode(
            application_name = f" · 团队招募 · {keyword} · {time_now}",
            table_head = table_recruit_head,
            table_body = "\n".join(contents)
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()