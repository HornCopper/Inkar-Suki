from pathlib import Path
from jinja2 import Template
from typing import List

from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import HTMLSourceCode

from ._template import template_dh, table_dunhao_head

import datetime

async def get_dh(type_: str) -> str | List[str | list] | None:
    url = f"https://www.j3dh.com/v1/h/data/hero?ifKnownDaishou=false&exterior={type_}&school=0&figure=0&page=0"
    data = (await Request(url).get()).json()
    if data["Code"] != 0:
        return "唔……API访问失败！"
    else:
        if data["Result"]["Heros"] is None:
            return "唔……没有获取到任何信息！"
        tables = []
        links = []
        floors = []
        num = 0
        for i in range(len(data["Result"]["Heros"])):
            x = data["Result"]["Heros"][i]
            post = x["PostId"]
            time_ = x["Time"]
            timestamp = datetime.datetime.strptime(time_, "%Y-%m-%dT%H:%M:%SZ")
            final_time = Time(int(timestamp.timestamp())).format("%m月%d日 %H:%M:%S")
            title = x["Details"]
            thread = x["BigPostId"]
            floor = x["Floor"]
            floors.append(floor)
            link = f"http://c.tieba.baidu.com/p/{thread}?pid={post}0&cid=0#{post}"
            links.append(link)
            tables.append(
                Template(template_dh).render(
                    num = str(i + 1),
                    context = title,
                    time = final_time
                )
            )
            num = num + 1
            if num == 10:
                break
        if len(tables) < 1:
            return "唔……没有获取到任何信息！"
        html = str(
            HTMLSourceCode(
                application_name = f" · 盆栽蹲号 · " + Time().format("%H:%M:%S"),
                table_head = table_dunhao_head,
                table_body = "\n".join(tables)
            )
        )
        final_path = await generate(html, "table", False)
        if not isinstance(final_path, str):
            return
        return [Path(final_path).as_uri(), links, floors]