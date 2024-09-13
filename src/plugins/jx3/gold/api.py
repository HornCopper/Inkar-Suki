from jinja2 import Template
from pathlib import Path

from src.tools.config import Config
from src.tools.basic.prompts import PROMPT
from src.tools.basic.server import server_mapping
from src.tools.utils.request import post_url, get_api
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.utils.time import get_current_time, convert_time
from src.tools.utils.file import read, write
from src.tools.generate import get_uuid, generate

import json

token = Config.jx3.api.token
bot_name = Config.bot_basic.bot_name_argument

async def demon_(server: str = "", group_id: str = ""):  # 金价 <服务器>
    goal_server = server_mapping(server, group_id)
    if not goal_server:
        return [PROMPT.ServerNotExist]
    
    data = await post_url("https://www.jx3mm.com/api/uniqueapi/Apiinterface/gettrade", json={"v": goal_server})
    data = json.loads(data)
    if "error" not in data:
        template_jinjia = """
        <tr>
            <td class="short-column">{{ date }}</td>
            <td class="short-column">{{ tieba }}</td>
            <td class="short-column">{{ _7881 }}</td>
            <td class="short-column">{{ wbl }}</td>
            <td class="short-column">{{ dd373 }}</td>
            <td class="short-column">{{ _5173 }}</td>
            <td class="short-column">{{ uu898 }}</td>
        </tr>"""
        types = {
            "tieba": "tieba",
            "7881": "_7881",
            "wanbaolou": "wbl",
            "dd373": "dd373",
            "5173": "_5173",
            "uu898": "uu898"
        }
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
            "tablecontent": "\n".join(tables),
            "server": goal_server,
            "app_time": convert_time(get_current_time(), "%H:%M:%S"),
            "saohua": "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！",
            "platforms": json.dumps(list(types), ensure_ascii=False).replace("wanbaolou", "万宝楼").replace("tieba", "贴吧").replace("dd", "DD").replace("uu", "UU"),
            "dates": json.dumps([each_price["date"] for each_price in data["data"]], ensure_ascii=False),
            "app_name": "金币价格"
        }

        for platform in types:
            input_data[types[platform]] = json.dumps([each_price[platform] for each_price in data["data"]], ensure_ascii=False)
        html = Template(read(VIEWS + "/jx3/trade/gold_v1.html")).render(**input_data)
    else:
        template_jinjia = """
        <tr>
            <td class="short-column">{{ date }}</td>
            <td class="short-column">{{ _7881 }}</td>
            <td class="short-column">{{ wbl }}</td>
            <td class="short-column">{{ dd373 }}</td>
            <td class="short-column">{{ _5173 }}</td>
            <td class="short-column">{{ uu898 }}</td>
        </tr>"""
        types = {
            "7881": "_7881",
            "WBL": "wbl",
            "DD373": "dd373",
            "5173": "_5173",
            "UU898": "uu898"
        }
        data = await get_api("https://spider2.jx3box.com/api/spider/gold/trend")
        server_data = data[goal_server]
        rows = []
        dates = []
        date_to_data = {}

        for platform_data in data[goal_server]["7881"]:
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
            "custom_font": ASSETS + "/font/custom.ttf",
            "tablecontent": "\n".join(tables),
            "server": goal_server,
            "app_time": convert_time(get_current_time(), "%H:%M:%S"),
            "saohua": "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！",
            "platforms": json.dumps(list(types), ensure_ascii=False).replace("WBL", "万宝楼"),
            "dates": json.dumps(dates, ensure_ascii=False),
            "app_name": "金币价格"
        }
        for platform in types:
            input_data[types[platform]] = json.dumps(platform_to_averages[types[platform]], ensure_ascii=False)
        html = Template(read(VIEWS + "/jx3/trade/gold_v2.html")).render(**input_data)
    
    final_html = CACHE + "/" + get_uuid() + ".html"
    write(final_html, html)
    final_path = await generate(final_html, False, "table", False)
    if not isinstance(final_path, str):
        return
    return Path(final_path).as_uri()