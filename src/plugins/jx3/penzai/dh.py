from src.tools.dep import *
from src.tools.utils import get_api

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
            table.append(template_dh.replace("$num", str(i + 1)).replace("$context", title).replace("$time", final_time))
            num = num + 1
            if num == 10:
                break
        if len(table) < 1:
            return "唔……没有获取到任何信息！"
        final_table = "\n".join(table)
        html = read(bot_path.VIEWS + "/jx3/trade/dunhao.html")
        font = bot_path.ASSETS + "/font/custom.ttf"
        saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
        saohua = saohua["data"]["text"]
        type_ = type_.replace(",", "+")
        html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f"蹲号 · {type_}")
        final_html = bot_path.CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        return [Path(final_path).as_uri(), links, floors]

