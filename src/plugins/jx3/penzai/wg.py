from urllib.parse import unquote
from pathlib import Path

from src.tools.utils.request import get_api, get_url
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.utils.file import read, write
from src.tools.generate import get_uuid, generate
from src.tools.utils.time import convert_time

import datetime
import re

template_wg = """
<tr>
    <td class="short-column">$num</td>
    <td class="short-column"><div id="context">$context</div></td>
    <td class="short-column">$place吧</td>
    <td class="short-column">$time</td>
</tr>
"""

async def get_from(url: str):
    data = await get_url(url)
    try:
        final = unquote(re.findall(r"<meta furl=\".+fname", data)[0][33:-16])
    except:
        final = "未知"
    return final

async def get_wg(name):
    timestamp = int(datetime.datetime.now().timestamp())
    data = await get_api(f"https://www.j3dh.com/v1/wg/data/exterior?exterior={name}&ignorePriceFlag=true&page=0&refresh=v1&time={timestamp}")
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
                final_time = convert_time(int(timestamp.timestamp()), "%m月%d日 %H:%M:%S")
                link = f"http://c.tieba.baidu.com/p/{thread}?pid={post}0&cid=0#{post}"
                place = await get_from(link)
                floor = x["Floor"]
                links.append(link)
                floors.append(floor)
                table.append(template_wg.replace("$num", str(i + 1)).replace("$context", title).replace("$time", str(final_time)).replace("$place", place))
                num = num + 1
                if num == 10:
                    break
            if len(table) < 1:
                return "唔……没有获取到任何信息！"
            final_table = "\n".join(table)
            html = read(VIEWS + "/jx3/trade/waiguan.html")
            font = ASSETS + "/font/custom.ttf"
            saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
            
            html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"贴吧物价 · {name}")
            final_html = CACHE + "/" + get_uuid() + ".html"
            write(final_html, html)
            final_path = await generate(final_html, False, "table", False)
            if not isinstance(final_path, str):
                return
            return [Path(final_path).as_uri(), links, floors]
