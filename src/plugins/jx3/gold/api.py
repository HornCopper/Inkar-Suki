from jinja2 import Template

from src.config import Config
from src.const.path import ASSETS, TEMPLATES
from src.utils.time import Time
from src.utils.network import Request
from src.utils.generate import generate
from src.utils.file import read
from src.templates import get_saohua

from ._template import template_jinjia, types

import json

token = Config.jx3.api.token
bot_name = Config.bot_basic.bot_name_argument

async def get_coin_price_image(server: str = ""):
    data = (await Request(f"{Config.jx3.api.url}/data/trade/demon?token={Config.jx3.api.token}&server={server}").get()).json()
    tables = []
    for each_price in data["data"]:
        tables.append(Template(template_jinjia).render(
            **
                {
                    "date": each_price["date"],
                    "tieba": each_price["tieba"],
                    "_7881": each_price["7881"],
                    "wbl": each_price["wanbaolou"],
                    "dd373": each_price["dd373"],
                    "_5173": each_price["5173"],
                    "uu898": each_price["uu898"]
                }
            )
        )
    
    input_data = {
        "custom_font": ASSETS + "/font/custom.ttf",
        "table_content": "\n".join(tables),
        "server": server,
        "app_time": Time().format("%H:%M:%S"),
        "saohua": get_saohua(),
        "platforms": json.dumps(list(types), ensure_ascii=False).replace("wanbaolou", "万宝楼").replace("tieba", "贴吧").replace("dd", "DD").replace("uu", "UU"),
        "dates": json.dumps([each_price["date"] for each_price in data["data"]], ensure_ascii=False),
        "app_name": "金币价格"
    }

    for platform in types:
        input_data[types[platform]] = json.dumps([each_price[platform] for each_price in data["data"]], ensure_ascii=False)
    html = Template(read(TEMPLATES + "/jx3/coin_trade.html")).render(**input_data)
    return await generate(html, "table", segment=True)