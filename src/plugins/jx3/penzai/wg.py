from urllib.parse import unquote
from pathlib import Path
from typing import List
from jinja2 import Template

from src.const.path import TEMPLATES, build_path
from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import template_wg, table_waiguan_head

import datetime
import re

async def get_tieba_source(url: str) -> str:
    data = (await Request(url).get()).text
    try:
        final = unquote(re.findall(r"<meta furl=\".+fname", data)[0][33:-16])
    except:
        final = "未知"
    return final

async def get_wg(name) -> str | None | List[str | list]:
    timestamp = int(datetime.datetime.now().timestamp())
    data = (await Request(f"https://www.j3dh.com/v1/wg/data/exterior?exterior={name}&ignorePriceFlag=true&page=0&refresh=v1&time={timestamp}").get()).json()
    if data["Code"] != 0:
        return "唔……API请求失败！"
    else:
        if data["Result"] == 0:
            return "没有请求到数据，请检查您的请求名称后重试？"
        else:
            links = []
            floors = []
            table = []
            num = 0
            for i in range(len(data["Result"]["Exteriors"])):
                x = data["Result"]["Exteriors"][i]
                time_ = x["Time"]
                thread = x["BigPostId"]
                post = x["PostId"]
                title = x["Details"]
                timestamp = datetime.datetime.strptime(time_, "%Y-%m-%dT%H:%M:%SZ")
                final_time = Time(int(timestamp.timestamp())).format()
                link = f"http://c.tieba.baidu.com/p/{thread}?pid={post}0&cid=0#{post}"
                place = await get_tieba_source(link)
                floor = x["Floor"]
                links.append(link)
                floors.append(floor)
                table.append(
                    Template(template_wg).render(
                        num = str(i + 1),
                        context = title,
                        time = str(final_time),
                        place = place
                    )
                )
                num = num + 1
                if num == 10:
                    break
            if len(table) < 1:
                return "唔……没有获取到任何信息！"
            html = str(
                HTMLSourceCode(
                    application_name = f" · 贴吧物价 · " + Time().format("%H:%M:%S"),
                    additional_js = Path(build_path(TEMPLATES, ["jx3", "waiguan.js"])),
                    table_head = table_waiguan_head,
                    table_body = "\n".join(table)
                )
            )
            final_path = await generate(html, "table", False)
            if not isinstance(final_path, str):
                return
            return [Path(final_path).as_uri(), links, floors]