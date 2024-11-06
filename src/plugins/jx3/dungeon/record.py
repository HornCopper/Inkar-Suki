from jinja2 import Template
from pathlib import Path

from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.templates import HTMLSourceCode

import time
import json

from ._template import (
    headers,
    template_item,
    table_item_head
)

async def get_item_record(name: str) -> str | Path:
    filter = {
        "Zone": "",
        "Srv": "",
        "Droppedi": name
    }
    params = {
        "sort": "Tm",
        "order": "desc",
        "limit": 30,
        "offset": 0,
        "_": int(time.time()) * 1000,
        "filter": json.dumps(filter, ensure_ascii=False),
        "op": "{\"Zone\":\"LIKE\",\"Srv\":\"LIKE\"}"
    }
    data = (await Request("https://www.jx3mm.com/jx3fun/jevent/jcitem", headers=headers, params=params).get()).json()
    if data["total"] == 0:
        return "未找到相关物品，请检查物品名称是否正确！"
    known_time = []
    known_id = []
    tables = []
    num = 0
    for i in data["rows"]:
        if i["Tm"] in known_time and i["Nike"] in known_id:
            continue
        known_time.append(i["Tm"])
        known_id.append(i["Nike"])
        id = i["Nike"]
        item_name = i["Droppedi"]
        if i["Copyname"][0:2] in ["英雄", "普通"]:
            zone = "25人" + i["Copyname"]
        else:
            zone = i["Copyname"]
        pick_time = Time(i["Tm"]).format()
        if not isinstance(pick_time, str):
            continue
        relate_time = Time().relate(i["Tm"])
        server = i["Srv"]
        tables.append(
            Template(template_item).render(
                server = server,
                name = item_name,
                map = zone,
                role = id,
                time = pick_time,
                relate = relate_time
            )
        )
        num += 1
        if num == 30:
            break
    if num == 0:
        return "未找到相关物品！"
    html = str(
        HTMLSourceCode(
            application_name=f" · 掉落统计 · 全服 · {name}",
            table_head = table_item_head,
            table_body = "\n".join(tables)
        )
    )
    path = await generate(html, "table", True)
    return Path(path)