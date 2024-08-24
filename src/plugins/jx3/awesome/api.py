from pathlib import Path

from src.tools.config import Config
from src.tools.utils.request import get_api
from src.tools.utils.time import convert_time, get_current_time
from src.tools.generate import get_uuid, generate
from src.tools.utils.file import read, write
from src.tools.utils.path import ASSETS, CACHE, VIEWS

token = Config.jx3.api.token

template_awesome = """
<tr>
    <td class="short-column">
        <strong>贴吧：</strong>$origin
        <br>
        <strong>服务器：</strong>$server
    </td>
    <td class="short-column">
        <strong>标题：</strong>$title
        <br>
        <strong>评论：</strong><div id="context">$comment</div>
        <br>
        <strong>时间：</strong>$time
    </td>
    <td class="short-column">$thread</td>
</tr>
"""

async def getAwesomeRecord(uin: str):
    api = f"{Config.jx3.api.url}/data/fraud/detail?token={token}&uid={uin}&uin={uin}"
    data = await get_api(api)
    if data["data"]["records"] == []:
        return False
    else:
        content = []
        for i in data["data"]["records"]:
            origin = i["tieba"]
            server = i["server"]
            for x in i["data"]:
                title = x["title"]
                thread = str(x["tid"])
                comment = x["text"]
                display_time = str(convert_time(x["time"]))
                comment = comment.replace(uin, "<span style=\"background-color: #f6c694\">" + uin + "</span>")
                template = template_awesome.replace("$origin", origin).replace("$server", server).replace("$title", title).replace("$comment", comment).replace("$time", display_time).replace("$thread", thread)
                content.append(template)
                if len(content) > 10:
                    break
        appinfo_time = convert_time(get_current_time(), "%H:%M:%S")
        appinfo = f" · 骗子查询 · {appinfo_time}"
        final_table = "\n".join(content)
        html = read(VIEWS + "/jx3/trade/cheater.html")
        font = ASSETS + "/font/custom.ttf"
        html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$appinfo", appinfo)
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        if not isinstance(final_path, str):
            return
        return Path(final_path).as_uri()