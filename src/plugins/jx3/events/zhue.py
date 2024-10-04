from pathlib import Path
from jinja2 import Template

from src.config import Config
from src.const.jx3.server import Server
from src.utils.time import Time
from src.utils.network import Request
from src.utils.generate import generate

from src.templates import HTMLSourceCode

from ._template import table_zhue_head, template_zhue

import json
import time

async def get_zhue_image(server: str):
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Microsoft Edge\";v=\"114\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Referer": "https://www.jx3mm.com/jx3fun/jevent/index.html"
    }
    filter = {
        "Zone": Server(server).zone,
        "Srv": server
    }
    base_params = {
        "sort": "Tm",
        "order": "desc",
        "limit": 30,
        "offset": 0,
        "_": int(time.time()) * 1000,
        "filter": json.dumps(filter, ensure_ascii=False),
        "op": "{\"Zone\":\"LIKE\",\"Srv\":\"LIKE\"}"
    }
    api = "https://www.jx3mm.com/jx3fun/jevent"
    data = (await Request(api, headers=headers, params=base_params).get()).json()
    data = data["rows"]
    tables = []
    for i in data:
        relateTime = Time().relate(i["Tm"])
        tables.append(
            Template(template_zhue).render(
                time = Time(i["Tm"]).format(),
                map = i["Content"],
                relate = relateTime
            )
        )
    html = str(
        HTMLSourceCode(
            application_name = " · 诛恶事件 · " + Time().format("%H:%M:%S"),
            table_head = table_zhue_head,
            table_body = "\n".join(tables)
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()