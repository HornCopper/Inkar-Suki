from jinja2 import Template
from pathlib import Path

from src.config import Config
from src.const.path import ASSETS, build_path
from src.utils.time import Time
from src.utils.network import Request
from src.utils.generate import get_uuid, generate
from src.templates import SimpleHTML

from ._template import template_jinjia, types

import json

token = Config.jx3.api.token
bot_name = Config.bot_basic.bot_name_argument

async def get_coin_price_image(server: str = ""):
    data = (await Request("https://spider2.jx3box.com/api/spider/gold/trend").get()).json()
    server_data = data[server]
    rows = []
    dates = []
    date_to_data = {}

    for platform_data in data[server]["7881"]:
        # 只拿日期，平台不影响
        dates.append(platform_data["date"])

    platform_to_averages = {param_name: [] for param_name in types.values()}

    for platform_name, param_name in types.items():
        if platform_name in server_data:
            platform_data = server_data[platform_name]
            for daily_data in platform_data:
                date = daily_data["date"]
                if date not in date_to_data:
                    date_to_data[date] = {}
                date_to_data[date][param_name] = round(daily_data["average"], 2)
                platform_to_averages[param_name].append(int(daily_data["average"]))

    sorted_dates = sorted(date_to_data.keys(), reverse=True)
    recent_dates = sorted_dates[:7]
    for date in recent_dates:
        row_data = date_to_data[date]
        row_data.update({"date": date})
        rows.append(row_data)

    tables = []
    for row in rows:
        tables.append(Template(template_jinjia).render(**row))

    input_data = {
        "custom_font": build_path(ASSETS, ["font", "custom.ttf"]),
        "tablecontent": "\n".join(tables),
        "server": server,
        "app_time": Time().format("%H:%M:%S"),
        "saohua": "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！",
        "platforms": json.dumps(list(types), ensure_ascii=False).replace("WBL", "万宝楼"),
        "dates": json.dumps(dates, ensure_ascii=False),
        "app_name": "金币价格"
    }
    for platform in types:
        input_data[types[platform]] = json.dumps(platform_to_averages[types[platform]], ensure_ascii=False)
    html = str(
        SimpleHTML(
            "jx3",
            "coin_trade",
            **input_data
        )
    )
    final_path = await generate(html, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()