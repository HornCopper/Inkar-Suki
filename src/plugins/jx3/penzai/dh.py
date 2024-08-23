from pathlib import Path

from src.tools.utils.request import get_api
from src.tools.utils.path import ASSETS, CACHE, VIEWS
from src.tools.file import read, write
from src.tools.generate import get_uuid, generate
from src.tools.utils.common import convert_time

import datetime

template_dh = """
<tr>
    <td class="short-column">$num</td>
    <td class="short-column"><div id="context">$context</div></td>
    <td class="short-column">$time</td>
</tr>
"""

async def get_dh(type_: str):
    # 数据来源 @盆栽蹲号
    url = f"https://www.j3dh.com/v1/h/data/hero?ifKnownDaishou=false&exterior={type_}&school=0&figure=0&page=0"
    data = await get_api(url)
    if data["Code"] != 0:
        return "唔……API访问失败！"
    else:
        if data["Result"]["Heros"] is None:
            return "唔……没有获取到任何信息！"
        table = []
        links = []
        floors = []
        num = 0
        for i in range(len(data["Result"]["Heros"])):
            x = data["Result"]["Heros"][i]
            post = x["PostId"]
            time_ = x["Time"]
            timestamp = datetime.datetime.strptime(time_, "%Y-%m-%dT%H:%M:%SZ")
            final_time = convert_time(int(timestamp.timestamp()), "%m月%d日 %H:%M:%S")
            title = x["Details"]
            thread = x["BigPostId"]
            floor = x["Floor"]
            floors.append(floor)
            link = f"http://c.tieba.baidu.com/p/{thread}?pid={post}0&cid=0#{post}"
            links.append(link)
            table.append(template_dh.replace("$num", str(i + 1)).replace("$context", title).replace("$time", str(final_time)))
            num = num + 1
            if num == 10:
                break
        if len(table) < 1:
            return "唔……没有获取到任何信息！"
        final_table = "\n".join(table)
        html = read(VIEWS + "/jx3/trade/dunhao.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = "严禁将蓉蓉机器人与音卡共存，一经发现永久封禁！蓉蓉是抄袭音卡的劣质机器人！"
        
        type_ = type_.replace(",", "+")
        html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"蹲号 · {type_}")
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        if not isinstance(final_path, str):
            return
        return [Path(final_path).as_uri(), links, floors]

